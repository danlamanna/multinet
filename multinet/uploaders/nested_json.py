"""Multinet uploader for nested JSON files."""
import itertools
import json

from .. import db, util

from flask import Blueprint, request

from typing import Tuple, List, Any

bp = Blueprint("nested_json", __name__)
bp.before_request(util.require_db)


def analyze_nested_json(
    raw_data: str, int_table_name: str, leaf_table_name: str
) -> Tuple[List[List[dict]], List[dict]]:
    """
    Transform nested JSON data into MultiNet format.

    `data` - the text of a nested_json file
    `(nodes, edges)` - a node and edge table describing the tree.
    """
    id = itertools.count(100)
    data = json.loads(raw_data)

    def keyed(rec: dict) -> dict:
        if "_key" in rec:
            return rec

        # keyed = dict(rec)
        rec["_key"] = str(next(id))

        return rec

    # The helper function will collect nodes and edges into these two lists.
    nodes: List[List[dict]] = [[], []]
    edges = []

    def helper(tree: dict) -> None:
        # Grab the root node of the subtree, and the child nodes.
        root = keyed(tree.get("node_data", {}))
        children = tree.get("children", [])

        # Capture the root node into one of two tables.
        if children:
            nodes[0].append(root)
        else:
            nodes[1].append(root)

        # Capture edges for each child.
        for child in children:
            # Grab the child data.
            child_data = keyed(child.get("node_data", {}))

            # Determine which table the child is in.
            child_table_name = (
                int_table_name if child.get("children") else leaf_table_name
            )

            # Record the edge record.
            edge = dict(child.get("edge_data", {}))
            edge["_from"] = f'{child_table_name}/{child_data["_key"]}'
            edge["_to"] = f'{int_table_name}/{root["_key"]}'
            edges.append(edge)

        # Recursively add the child subtrees.
        for child in children:
            helper(child)

    # Kick off the analysis.
    helper(data)
    return (nodes, edges)


@bp.route("/<workspace>/<table>", methods=["POST"])
def upload(workspace: str, table: str) -> Any:
    """
    Store a nested_json tree into the database in coordinated node and edge tables.

    `workspace` - the target workspace.
    `table` - the target table.
    `data` - the nested_json data, passed in the request body.
    """
    # Set up the parameters.
    data = request.data.decode("utf8")
    space = db.db(workspace)
    edgetable_name = f"{table}_edges"
    int_nodetable_name = f"{table}_internal_nodes"
    leaf_nodetable_name = f"{table}_leaf_nodes"

    # Set up the database targets.
    if space.has_collection(edgetable_name):
        edgetable = space.collection(edgetable_name)
    else:
        edgetable = space.create_collection(edgetable_name, edge=True)

    if space.has_collection(int_nodetable_name):
        int_nodetable = space.collection(int_nodetable_name)
    else:
        int_nodetable = space.create_collection(int_nodetable_name)

    if space.has_collection(leaf_nodetable_name):
        leaf_nodetable = space.collection(leaf_nodetable_name)
    else:
        leaf_nodetable = space.create_collection(leaf_nodetable_name)

    # Analyze the nested_json data into a node and edge table.
    (nodes, edges) = analyze_nested_json(data, int_nodetable_name, leaf_nodetable_name)

    # Upload the data to the database.
    edgetable.insert_many(edges)
    int_nodetable.insert_many(nodes[0])
    leaf_nodetable.insert_many(nodes[1])

    return dict(
        edgecount=len(edges), int_nodecount=len(nodes[0]), leaf_nodecount=len(nodes[1])
    )
