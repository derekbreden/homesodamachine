import time, sys
t0=time.time()
import cadquery as cq
import vtk
from vtkmodules.vtkRenderingCore import vtkRenderer, vtkRenderWindow, vtkPolyDataMapper, vtkActor, vtkWindowToImageFilter
from vtkmodules.vtkIOImage import vtkPNGWriter
print(f"imports {time.time()-t0:.2f}s", flush=True)

path = sys.argv[1]
t=time.time()
shape = cq.importers.importStep(path)
print(f"importStep {time.time()-t:.2f}s", flush=True)

solids = shape.val().Solids() if hasattr(shape,'val') else []
print(f"solids={len(solids)}", flush=True)

t=time.time()
pd = shape.val().toVtkPolyData(tolerance=0.1, angularTolerance=0.3)
print(f"toVtkPolyData {time.time()-t:.2f}s  points={pd.GetNumberOfPoints()} cells={pd.GetNumberOfCells()}", flush=True)

t=time.time()
ren = vtkRenderer(); ren.SetBackground(0.102,0.102,0.180)
rw = vtkRenderWindow(); rw.SetOffScreenRendering(1); rw.AddRenderer(ren); rw.SetSize(400,400)
m = vtkPolyDataMapper(); m.SetInputData(pd)
a = vtkActor(); a.SetMapper(m); ren.AddActor(a)
ren.ResetCamera()
rw.Render()
w2i = vtkWindowToImageFilter(); w2i.SetInput(rw); w2i.Update()
wr = vtkPNGWriter(); wr.SetFileName("/tmp/_vtk_probe.png"); wr.SetInputConnection(w2i.GetOutputPort()); wr.Write()
print(f"vtk offscreen render+write {time.time()-t:.2f}s", flush=True)
print(f"TOTAL {time.time()-t0:.2f}s")
