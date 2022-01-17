```
(venv) nikhil-mba:benchmarks Nikhil$ ./benchmark.sh 5000
[vishnubob] mean read+parse time (n=5000): 0.000781396484375
[music21] mean read+parse time (n=5000): 0.00084384765625
[mido] mean read+parse time (n=5000): 0.0007716796875
[tonejs] mean read+parse time (n=5000): 0.0624
```

(mean time in millis)

pretty significant difference between js and python parsers

among python parsers, not too much difference. prefer `music21`, `mido` over `python-midi` since they are better supported