from . import voroplusplus

def compute_voronoi(points, limits, dispersion, radii=[], periodic=[False]*3):
  """
Input arg formats:
  points = list of 3-vectors (lists or compatible class instances) of doubles,
    being the coordinates of the points to Voronoi-tessellate.
  limits = 3-list of 2-lists, specifying the start and end sizes of the box the
    points are in.
  dispersion = max distance between two points that might be adjacent (sets
    voro++ block sizes.)
  radii (optional) = list of python floats as the sphere radii of the points,
    for radical (weighted) tessellation.
  periodic (optional) = 3-list of bools indicating x, y and z periodicity of 
    the system box.
  
Output format is a list of cells as follows:
  [ # list in same order as original points.
    {
      'volume' : 1.0,
      'vertices' : [[1.0, 2.0, 3.0], ...], # positions of vertices
      'adjacency' : [[1,3,4, ...], ...], # cell-vertices adjacent to i by index
      'faces' : [
        {
          'vertices' : [7,4,13, ...], # vertex ids in loop order
          'adjacent_cell' : 34 # *cell* id, negative if a wall
        }, ...]
      'original' : point[index] # the original instance from args
    },
    ... 
  ]
  
  NOTE: The class from items in input points list is reused for all 3-vector
  outputs. It must have a constructor which accepts a list of 3 python floats
  (python's list type does satisfy this requirement.)
  """
  return voroplusplus.compute_voronoi(points, limits, dispersion, radii, periodic)

def compute_2d_voronoi(points, limits, dispersion, radii=[], periodic=[False]*2, z_height=0.5):
  """Input arg formats:
  points = list of 2-vectors (lists or compatible class instances) of doubles,
    being the coordinates of the points to Voronoi-tessellate.
  limits = 2-list of 2-lists, specifying the start and end sizes of the box the
    points are in.
  dispersion = max distance between two points that might be adjacent (sets
    voro++ block sizes.)
  radii (optional) = list of python floats as the circle radii of the points,
    for radical (weighted) tessellation.
  periodic (optional) = 2-list of bools indicating x and y periodicity of 
    the system box.
  z_height = a suitable system-size dimension value (if this is particularly different to the
    other system lengths, voro++ will be very inefficient.)
  
Output format is a list of cells as follows:
  [ # list in same order as original points.
    {
      'volume' : 1.0, # in fact, in 2D, this is the area.
      'vertices' : [[1.0, 2.0], ...], # positions of vertices
      'adjacency' : [[1,3], ...], # cell-vertices adjacent to i by index
      'faces' : [
        {
          'vertices' : [7,4], # vertex ids, always 2 for a 2D cell edge.
          'adjacent_cell' : 34 # *cell* id, negative if a wall
        }, ...]
      'original' : point[index] # the original instance from args
    },
    ... 
  ]"""
  vector_class = voroplusplus.get_constructor(points[0])
  points = [list(p) for p in points]
  points3d = [p[:] +[0.] for p in points]
  limits3d = [l[:] for l in limits] + [[-z_height, +z_height]]
  periodic = periodic + [False]
  
  py_cells3d = voroplusplus.compute_voronoi(points3d, limits3d, dispersion, radii, periodic)
  
  # we assume that each cell is a prism, and so the 2D solution for each cell contains
  # half of the vertices from the 3D solution. We verify this assumption by asserting
  # that each cell has a face adjacent to both -5 and -6, and that they don't share
  # any vertices. We simply take the -5 cell, and ignore the z components.
  
  py_cells = []
  depth = z_height * 2
  
  for p3d in py_cells3d:
    faces_to = [f['adjacent_cell'] for f in p3d['faces']]
    assert(-5 in faces_to and -6 in faces_to)
    vertices_to_keep = p3d['faces'][faces_to.index(-5)]['vertices']
    
    faces2d = []
    for f in p3d['faces']:
      if f['adjacent_cell'] == -5 or f['adjacent_cell'] == -6:
        continue
      faces2d.append({
        'adjacent_cell':f['adjacent_cell'],
        'vertices' : [vertices_to_keep.index(vid) for vid in f['vertices'] if vid in vertices_to_keep]
      })
    
    py_cells.append({
      'faces' : faces2d,
      'original' : vector_class(p3d['original'][:-1]),
      'vertices' : [vector_class(p3d['vertices'][v][:-1]) for v in vertices_to_keep],
      'volume' : p3d['volume'] / depth
    })
    
    adj = [[len(vertices_to_keep)-1, 1]]
    for i in range(1, len(vertices_to_keep)-1):
      adj.append([i-1, i+1])
    adj.append([len(vertices_to_keep)-2, 0])
      
    py_cells[-1]['adjacency'] = adj
  
  return py_cells


def plot_3d_cells(data, random_cell_colors=True, line3d_kwargs = {}, poly3d_kwargs = {}, scatter_kwargs = {}, **kwargs ):
    """
    Plot the cells given the data supplied by the function `pyvoro.compute_voronoi`. 
    
    Inputs
    ------
    - data: list of dicts. Output of function `pyvoro.compute_voronoi`.
    - random_cell_colors = True. Assign random colors to the different cells.
    - line3d_kwargs: Arguments for Line3DCollection
    - poly3d_kwargs: Arguments for Poly3DCollection
    - scatter_kwargs: Arguments for plt.scatter
    - kwargs: in case the previous kwargs are not used, the function will try to extract them from kwarg. But this might generate using the common kwargs for all functions.
    
    Output
    ------
    - None
    
    """

    # Importing
    import inspect
    import numpy as np
    from matplotlib import pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection, Line3DCollection
    
    # filtering the args to the different plotting functions:
    if not line3d_kwargs: 
        line3d_args = [k for k, v in inspect.signature(Line3DCollection).parameters.items()]
        line3d_kwargs = {k: kwargs.pop(k) for k in dict(kwargs) if k in line3d_args}

    if not poly3d_kwargs: 
        poly3d_args = [k for k, v in inspect.signature(Poly3DCollection).parameters.items()]
        poly3d_kwargs = {k: kwargs.pop(k) for k in dict(kwargs) if k in poly3d_args}

    if not scatter_kwargs: 
        scatter_args = [k for k, v in inspect.signature(plt.scatter).parameters.items()]
        scatter_kwargs = {k: kwargs.pop(k) for k in dict(kwargs) if k in scatter_args}

    for each_cell in data: 
        vertices = each_cell['vertices'] 
        faces = each_cell['faces']

        vertices_in_cell = []

        for each_face in faces: 
            vertices_face = each_face['vertices']
            sub_faces_ = []

            for each_vert in vertices_face:
                sub_faces_.append(tuple(vertices[each_vert]))

            # Vertices
            vertices_in_cell.append(sub_faces_)

            # Lines 
            lines_=[]
            for init_vert,final_vert in zip(vertices_face[:-1],vertices_face[1:]):
                lines_.append([
                                vertices[init_vert], # Initial point of the line. 
                                vertices[final_vert] # Final point of the line
                                ])            

            # Appending the last segment which close the line. 
            lines_.append([vertices[vertices_face[-1]],vertices[vertices_face[0]]]) 

            # Plotting all lines in the face. 
            ax.add_collection3d(Line3DCollection(lines_, **line3d_kwargs))

        # Plotting the vertex independently 
        x = [each_[0] for each_ in vertices]
        y = [each_[1] for each_ in vertices]
        z = [each_[2] for each_ in vertices]

        # Plotting all vertices in each cell
        ax.scatter(x,y,z, **scatter_kwargs)

        # Plotting all faces in each cell
        if random_cell_colors:
            ax.add_collection3d(Poly3DCollection(vertices_in_cell, **poly3d_kwargs , facecolors=np.random.rand(3,)))
        else:
            ax.add_collection3d(Poly3DCollection(vertices_in_cell, **poly3d_kwargs))
