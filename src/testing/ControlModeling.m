clear; clc

values = [0, 0.1, 0.19, 0.271, 0.34390000000000004, 0.40951000000000004, 0.46855900000000006, 0.5217031000000001, 0.5695327900000001, 0.6125795110000001, 0.6513215599000001, 0.68618940391, 0.717570463519, 0.7458134171671, 0.7712320754503901, 0.7941088679053511, 0.814697981114816, 0.8332281830033343, 0.8499053647030009, 0.8649148282327008, 0.8784233454094308, 0.8905810108684877, 0.901522909781639, 0.911370618803475, 0.9202335569231275, 0.9282102012308148, 0.9353891811077333, 0.94185026299696, 0.947665236697264, 0.9528987130275376, 0.9576088417247839, 0.9618479575523055, 0.9656631617970749, 0.9690968456173674, 0.9721871610556306, 0.9749684449500675, 0.9774716004550608, 0.9797244404095546, 0.9817519963685992, 0.9835767967317393, 0.9852191170585654, 0.9866972053527088, 0.9880274848174379, 0.9892247363356941, 0.9903022627021246, 0.9912720364319122, 0.992144832788721, 0.9929303495098489, 0.9936373145588641, 0.9942735831029776];
times = [0.0, 0.006553173065185547, 0.11162018775939941, 0.21674227714538574, 0.3193783760070801, 0.42449522018432617, 0.5296173095703125, 0.6347463130950928, 0.739915132522583, 0.8451621532440186, 0.950998067855835, 1.0541701316833496, 1.1551554203033447, 1.260324239730835, 1.3605303764343262, 1.4657042026519775, 1.5690841674804688, 1.673685073852539, 1.778780221939087, 1.883925199508667, 1.9882092475891113, 2.0903751850128174, 2.19208025932312, 2.2971842288970947, 2.400268077850342, 2.5048530101776123, 2.60901141166687, 2.7135872840881348, 2.8187901973724365, 2.9241013526916504, 3.0269744396209717, 3.1283462047576904, 3.231260299682617, 3.333256244659424, 3.4344980716705322, 3.537135124206543, 3.642430305480957, 3.7428252696990967, 3.843297243118286, 3.945725202560425, 4.05121111869812, 4.155781269073486, 4.260042190551758, 4.365529298782349, 4.46709132194519, 4.569538116455078, 4.674771308898926, 4.779924154281616, 4.884353160858154, 4.989914178848267];

mdl = @

plot(times, values, 'o')