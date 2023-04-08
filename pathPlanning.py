# Import necessary libraries
from networkx import Graph
from shapely.geometry import Polygon, Point, LineString
import numpy as np
import heapq

import yaml
import argparse

import matplotlib.pyplot as plt
import matplotlib.patches as patch

import logging
import coloredlogs

# Dataclass to store priority queue element for Dijkstra's algorithm
from dataclasses import dataclass, field, astuple
from typing import List, Set, Tuple, Optional


def setupLogger():
    # Configure the logging system
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(levelname)s: %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')

    coloredlogs.install(
        level='INFO', fmt='%(asctime)s %(levelname)s: %(message)s')


# Define the data structure for a configuration file
@dataclass
class InputData:
    x_start: float
    y_start: float
    x_goal: float
    y_goal: float
    x_space_size: float
    y_space_size: float
    list_obstacles: List[List[List[float]]]


# Define the data structure for a priority queue element in Dijkstra's algorithm
@dataclass(order=True)
class PQElement:
    """
    Dataclass representing an element of a priority queue in Dijkstra's algorithm.

    Parameters:
    -----------
    cost: float
        The cost associated with the path to reach the current node.
    current: Point
        The current node.
    path: List[Point]
        The list of nodes visited to reach the current node.

    Notes:
    ------
    This class is ordered based on the cost attribute only, as there is no need to compare the current or path attributes.
    Comparing only the cost attribute avoids unnecessary comparisons when the cost is the same for two paths.
    """
    cost: float
    current: Point = field(compare=False)
    path: List[Point] = field(compare=False)

    def __iter__(self):
        return iter(astuple(self))


# Define helper functions


def getArguments():
    # Define command line arguments
    parser = argparse.ArgumentParser(
        prog='shortestPathFinding', description='Find the Shortest Path that avoids obstacles')
    parser.add_argument(
        'inputyaml', help='input YAML file containing problem description')
    parser.add_argument('output', nargs='?',
                        default='solution.txt', help='output file path')
    parser.add_argument('--plot', action='store_true',
                        help='plot the solution')
    args = parser.parse_args()

    return args


def plotPath(start: Point, goal: Point, polygons: List[Polygon], path: List[Point], inputData: InputData, show=False):
    # Create a new figure and axes
    fig, ax = plt.subplots()

    for i, polygon in enumerate(polygons):
        ax.fill(*polygon.exterior.xy, label=f"polygon {i}")

    xs = [point.x for point in path]
    ys = [point.y for point in path]

    ax.plot(xs, ys, '.-', label="path")

    ax.scatter(*start.xy, label="start")
    ax.scatter(*goal.xy, label="goal")

    # Set the x and y limits of the plot to match the problem space size
    ax.set_xlim([0, inputData.x_space_size])
    ax.set_ylim([0, inputData.y_space_size])

    leg = ax.legend()

    # Save the plot to a PNG file and show it
    plt.savefig('solution.png')
    if show:
        plt.show()


# Main Helpers

def polygonsIntersect(polygons: List[Polygon]) -> bool:
    """
    Checks whether any polygon intersect other one     
    """
    for i, polygon1 in enumerate(polygons[:-1]):
        for polygon2 in polygons[i+1:]:
            if polygon1.intersects(polygon2):
                return True
    return False


def startGoalInsideObstacles(start: Point, goal: Point, polygons: List[Polygon]) -> bool:
    """
    Checks whether any polygon intersect the start or goal
    """
    for polygon in polygons:
        if polygon.contains(start) or polygon.contains(goal):
            return True
    return False


def generateVisibilityGraph(start: Point, goal: Point, polygons: List[Polygon]) -> Graph:
    graph = Graph()
    # Create a list of vertices consisting of start point, goal point, and all vertices of the polygons
    vertices = [start, goal] + \
        [vertex for polygon in polygons for vertex in polygon.exterior.coords[:-1]]

    # Create edges between all pairs of vertices that have a line of sight
    for i, vertex1 in enumerate(vertices[:-1]):
        for vertex2 in vertices[i + 1:]:
            p1, p2 = Point(vertex1), Point(vertex2)
            if line_of_sight(p1, p2, polygons):
                # Add edge between p1 and p2 with weight equal to distance between them
                graph.add_edge(p1, p2, weight=p1.distance(p2))

    return graph


def line_of_sight(p1: Point, p2: Point, polygons: List[Polygon]) -> bool:
    """
    Checks whether there is a line of sight between two points
    avoiding polygons in the environment
    """
    line = LineString([p1, p2])
    for polygon in polygons:
        if line.crosses(polygon) or polygon.contains(line):
            return False
    return True


def dijkstra(graph: Graph, start: Point, goal: Point, world: Polygon) -> Optional[List[Point]]:
    """
    Dijkstra's algorithm for finding the shortest path between two points
    in a graph
    """

    pq: List[PQElement] = [
        PQElement(0, start, [])]  # Create priority queue element with start point

    visited: Set[Point] = set()  # Keep track of visited points

    while pq:
        cost: float
        current: Point
        path: List[Point]
        # Get the smallest element from priority queue based on cost only
        (cost, current, path) = heapq.heappop(pq)

        if current in visited:  # If the current point has already been visited, skip it
            continue

        visited.add(current)  # Add current point to visited set
        path = path + [current]  # Add current point to path

        if current == goal:  # If current point is the goal point, return the path
            return path
        # Iterate over the neighbors of the current point
        for neighbor in graph[current]:
            if neighbor not in visited:  # If the neighbor has not been visited
                # if not neighbor.intersects(world):
                #     return None  # Point is outside the boundaries
                heapq.heappush(
                    pq, PQElement(cost + graph[current][neighbor]["weight"], neighbor, path))  # Add neighbor to the priority queue

    return None  # If no path is found, return None


def calculatePath() -> Optional[List[List[float]]]:
    args = getArguments()
    # Load input from YAML file
    try:
        inputDataDict = yaml.load(open(args.inputyaml), yaml.Loader)
        inputData = InputData(**inputDataDict)
    except Exception as e:
        logging.exception("🚨 Missing configuration: %s", str(e))
        raise e

    # Environment definition
    start = Point(inputData.x_start, inputData.y_start)
    goal = Point(inputData.x_goal, inputData.y_goal)

    polygons = [Polygon(obstacle) for obstacle in inputData.list_obstacles]

    world = Polygon([(0, 0), (0, inputData.y_space_size), (inputData.x_space_size,
                    inputData.y_space_size), (inputData.x_space_size, 0)])
    # Check if polygons intersect
    if polygonsIntersect(polygons):
        logging.exception("🚨 Polygons intersect: Change configuration file")
        raise Exception("🚨 Polygons intersect")

    # Check if start or goal inside polygons
    if startGoalInsideObstacles(start, goal, polygons):
        logging.exception(
            "🚨 Polygons intersect start or goal: Change configuration file")
        raise Exception("🚨  Polygons intersect start or goal")
    # # Compute the shortest path

    logging.info("⏳ Generating graph...")
    graph = generateVisibilityGraph(start, goal, polygons)
    logging.info("✅ Graph generated")

    # Compute the shortest path from start to goal using Dijkstra's algorithm
    logging.info("⏳ Calculating graph...")
    path = dijkstra(graph, start, goal, world)
    logging.info("✅ Path Calculated")

    # Visualize if --plot argument is provided
    if path:
        listPath = list(
            map(lambda point: (point.xy[0] + point.xy[1]).tolist(), path))
        logging.info("✨ Path found: %s", str(path))
        logging.info("✨ Result: %s", str(listPath))

        plotPath(start, goal, polygons, path, inputData, show=bool(args.plot))

        return listPath

    else:
        logging.error("😕 No path found")
        raise Exception("😕 No path found")


if __name__ == "__main__":
    setupLogger()
    calculatePath()
