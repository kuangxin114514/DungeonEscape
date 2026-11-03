import sys, time
sys.path.insert(0, r"C:\Program Files\Epic Games\UE_4.27\Engine\Plugins\Experimental\PythonScriptPlugin\Content\Python")
import remote_execution as re
# read run_command signature / source hints
import inspect
print(inspect.getsource(re.RemoteExecution.run_command)[:1500])
