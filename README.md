# AcqPack
[![doc-status](https://readthedocs.org/projects/acqpack/badge/?version=latest)](http://acqpack.readthedocs.io/en/latest/?badge=latest)   
[![linux-status](https://travis-ci.org/FordyceLab/AcqPack.svg?branch=master)](https://travis-ci.org/FordyceLab/AcqPack) Linux

Code to perform acquisitions (experiment automation and hardware control).
Should be combined with MMCorePy for microscope control.

-`config/` should be for computer scope settings   
-`setup/` should be for experiment scope settings

`from acqpack import ...`
```
Autosampler::
	xy
	z
	frames
		transform
		position_table
	add_frame()
	add_plate()
	home()
	goto()
	where()
	exit()
 
FractionCollector::
	xy
	frames
		transform
		position_table
	add_frame()
	add_plate()
	home()
	goto()
	where()
	exit()
 
Motor::
	config
	serial
	initialize()
	cmd()
	is_busy()
	set_velocity()
	halt()
	home()
	goto()
	move_relative()
	exit()
 
AsiController::
	config
	serial
	initialize()
	cmd()
	halt()
	cmd_xy()
	is_busy_xy()
	halt_xy()
	where_xy()
	goto_xy()
	move_relative_xy()
	cmd_z()
	is_busy_z()
	halt_z()
	where_z()
	goto_z()
	move_relative_z()
	exit()
 
Manifold::
	client
	read_offset
	valvemap
	read_valve()
	pressurize()
	depressurize()
	close()
	open()
	load_valvemap()
	exit()
 
utils/
	read_delim()
	read_delim_pd()
	lookup()
	generate_position_table()
	spacing()
	load_mm_positionlist()
	generate_grid()
 
gui/
	snap()
	video()
	grid()
	manifold_control()
	stage_control()
```






	



