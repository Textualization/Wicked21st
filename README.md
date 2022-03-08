# Wicked 21st Board Game Simulations


## Configuration files

`config.py`

* Seed
* Number of runs
* Graph to use
* Verbose
* Starting crisis count
* Length of game
* Crisis check
* Crisis rising


## Running

* `full_simul1.py` -- run one game, using the SEED in config. Number of players passed command-line
* `full_simul.py` -- run config NUM_RUNS for the number of players in command-line

### Using simul for param setting

```bash
cp config.py config.py.base
rm -f generated/stats.txt
for CHECK in 4 5 6 7
do
   export CHECK
   for RISING in 3 4 5
   do
      export RISING
      cat config.py.base | perl -ne 'if(m/_CHECK/){print "CRISIS_CHECK=".$ENV{CHECK}."\n"}elsif(m/_RISING/){print "CRISIS_RISING=".$ENV{RISING}."\n"}elsif(m/VERBOSE/){print"VERBOSE=False\n"}else{print}' > config.py
      for PL in 3 4 5 6
      do
         python3 full_simul.py $PL | tail -1 >> generated/stats.txt
      done
   done
done
mv config.py.base config.py
```

## Graph maintenance

* `python3 graph_to_cascades.py maps/map20220124.json temp.json; mv temp.json maps/map20220124.json` -- recompute cascading scores
* `python3 graph_to_tsv.py maps/map20220124.json > maps/map20220124.tsv` -- generate TSV (transform to spreadsheet and upload to google docs)
* `python3 show_graph.py maps/map20220124.json 1 > generated/graph.dot; cd generated; dot -Tpng graph.dot > graph.png; dot -Tsvg graph.dot > graph.svg` -- generate graphviz rendering
* `python3 graph_to_7boards.py; cd generated; for d in board_*.dot; do dot -Tpng $d > ${d%%.dot}.png; dot -Tsvg $d > ${d%%.dot}.svg; done` -- produce the 7-board rendering

* `old_graph_to_new_graph.py` -- no longer used

## Experiments

* `cascade_instructions.py` -- no longer used

