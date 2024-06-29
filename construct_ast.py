import os
import tree_sitter
import tree_sitter_python as tspython
from tree_sitter import Language, Parser
import ast
import networkx as nx
import matplotlib.pyplot as plt
import plotly.graph_objects as go

PY_LANGUAGE = Language(tspython.language())

# Load Tree-sitter Python language module
# tree_sitter_python = tree_sitter.Language('build/tree-sitter-python.so', 'python')

class CreateTree:
    def __init__(self, code, file_path):
        self.parser = Parser(PY_LANGUAGE)
        self.tree_nx = nx.DiGraph()
        self.code = code
        self.file_path = file_path 
    
    def parse_ast(self):
        """
        Parse the code using the Tree-sitter parser.
        """
        tree = self.parser.parse(bytes(self.code, "utf-8"))
        return tree
    
    def point_to_byte_offset(self, point):
        """
        Convert a Point(row, column) to a byte offset.
        """
        lines = self.code.splitlines(True)
        byte_offset = sum(len(lines[i]) for i in range(point.row)) + point.column
        return byte_offset

    def get_node_text(self, start_point, end_point):
        """
        Extract code between start_point and end_point.
        """
        start_byte = self.point_to_byte_offset(start_point)
        end_byte = self.point_to_byte_offset(end_point)
        ans = self.code[start_byte:end_byte]
        return str(ans)

    def add_node_with_attribute(self, func_node):
        """ 
        Add a node to the graph with the function name and parameters as attributes.
        """
        name = func_node.child_by_field_name('name').text.decode('utf-8')
        params_node = func_node.child_by_field_name('parameters')
        params_list = [param.text.decode('utf-8') for param in params_node.children if param.text.decode('utf-8') not in ('(', ')', ',')]
        self.tree_nx.add_node(name, params=params_list, func_node=func_node)
        # G.nodes[name]['params'] = params

    def add_edge_with_attribute(self, caller, callee):
        """ 
        Add an edge to the graph with the callee function name and its arguments as attributes.
        """
        name = caller.child_by_field_name('name').text.decode('utf-8')
        target = callee.child_by_field_name('function').text.decode('utf-8')
        # G.add_edge(name, target)
        args_node = callee.child_by_field_name('arguments')
        args_list = [i.text.decode('utf-8') for i in args_node.children if i.text.decode('utf-8') not in ('(', ')', ',')]
        self.tree_nx.add_edge(name, target, args=args_list, node=callee)
        

    def call_graph(self):
        """ 
        Construct a call graph of functions only from the code.
        """
        tree = self.parser.parse(bytes(self.code, "utf-8"))
        root = tree.root_node
        functions_query = PY_LANGUAGE.query("(function_definition) @function") 
        calls_query = PY_LANGUAGE.query("(call) @call")
        functions = functions_query.captures(root) 
        # G = nx.DiGraph()
        # print(functions)
        list_functions = []
        for func, _ in functions:
            list_functions.append(func.child_by_field_name('name').text.decode('utf-8'))
            calls = calls_query.captures(func) 
            self.add_node_with_attribute(func)
            for callee, _ in calls:
                # print(callee)
                self.add_edge_with_attribute(func, callee)
        return self.tree_nx, list_functions
    
    def get_function_from_name(self, name):
        """ 
        Get the function code from the function name.
        """
        try:
            st = self.tree_nx.nodes[name]['func_node'].start_point
            en = self.tree_nx.nodes[name]['func_node'].end_point
            func = self.get_node_text(st, en)
            return func
        except KeyError as e:
            print(f"Error: The function name '{name}' does not exist in the tree. Please check the function name and try again.")
            print(f"KeyError: {e}")
            return None
    
    def get_st_and_end_points(self, name):
        """ 
        Get the start and end points of the function from the function name.
        """
        try:
            st = self.tree_nx.nodes[name]['func_node'].start_point
            en = self.tree_nx.nodes[name]['func_node'].end_point
            return (st,en)
        except KeyError as e:
            print(f"Error: The function name '{name}' does not exist in the tree. Please check the function name and try again.")
            print(f"KeyError: {e}")
            return None
        
    def get_callers(self, function_name):
        """ 
        Get the list of functions that call the given function.
        """
        if function_name not in self.tree_nx:
            print(f"Function {function_name} does not exist in the call graph.")
            return []
        callers = list(self.tree_nx.predecessors(function_name))
        return callers
    
    def get_callers_function_code(self, function_name):
        """ 
        Get the code of all the functions that call the given function.
        """
        list_callers = self.get_callers(function_name)
        code_list = []
        for caller in list_callers:
            code_list.append(self.get_function_from_name(caller))
        return code_list
    
        
    def update_tree(self, code):
        """ 
        Update the tree with the new code.
        """
        self.code = code
        self.tree_nx , list_ = self.call_graph()
        # return self.tree_nx , list_
            

    def draw_graph(self):
        """ 
        Draw the call graph using NetworkX and Plotly.
        """
        node_labels = {}
        for n in self.tree_nx.nodes():
            if 'params' in self.tree_nx.nodes[n]:
                node_labels[n] = f"{n}\n{self.tree_nx.nodes[n]['params']}"
            else:
                node_labels[n] = str(n)  # Fallback label if 'params' is missing or empty

        edge_labels = {e: f"{self.tree_nx.edges[e]['args']}" for e in self.tree_nx.edges()}
        # Kamada-Kawai layout
        pos = nx.kamada_kawai_layout(self.tree_nx)

        # Create plotly scatter plot for nodes
        node_x = []
        node_y = []
        for node in self.tree_nx.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)

        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            text=[node_labels[n] for n in self.tree_nx.nodes()],
            textposition='top center',
            marker=dict(size=20, color='skyblue', line=dict(width=2)),
            hoverinfo='text'
        )

        # Create plotly scatter plot for edges
        edge_x = []
        edge_y = []
        annotations = []
        for edge in self.tree_nx.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.append(x0)
            edge_x.append(x1)
            edge_x.append(None)
            edge_y.append(y0)
            edge_y.append(y1)
            edge_y.append(None)

            # Calculate the position and direction for the arrowhead
            arrow_x = x1
            arrow_y = y1
            arrow_dx = x1 - x0
            arrow_dy = y1 - y0

            annotations.append(
                dict(
                    x=arrow_x,
                    y=arrow_y,
                    ax=x0,
                    ay=y0,
                    xref='x',
                    yref='y',
                    axref='x',
                    ayref='y',
                    showarrow=True,
                    arrowhead=3,
                    arrowsize=2,
                    arrowwidth=1,
                    arrowcolor='black'
                )
            )

        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=2, color='black'),
            hoverinfo='none',
            mode='lines'
        )

        # Create plotly scatter plot for edge labels
        edge_label_trace = go.Scatter(
            x=[(pos[edge[0]][0] + pos[edge[1]][0]) / 2 for edge in self.tree_nx.edges()],
            y=[(pos[edge[0]][1] + pos[edge[1]][1]) / 2 for edge in self.tree_nx.edges()],
            mode='text',
            text=[edge_labels[edge] for edge in self.tree_nx.edges()],
            textposition='top center',
            textfont=dict(color='red', size=12)
        )

        # Create figure with title and annotations
        fig = go.Figure(data=[edge_trace, node_trace, edge_label_trace],
                        layout=go.Layout(
                            title=self.file_path,  # Add your title here
                            showlegend=False,
                            hovermode='closest',
                            margin=dict(b=20, l=5, r=5, t=40),
                            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                            height=800,  # Adjust height as needed
                            annotations=annotations
                        ))

        fig.show()