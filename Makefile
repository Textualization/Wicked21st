all: walkthrough.txt

7boards: config.py graph_to_7boards.py show_graph.py Makefile
	python3 graph_to_7boards.py
	cd generated; for f in board_*.dot; do circo -Tpng $$f > `basename -s .dot $$f`.png; done

walkthrough.txt: ./wicked21st/game.py ./wicked21st/techtree.py ./wicked21st/project.py ./show_graph.py Makefile
	grep '###' ./wicked21st/game.py|perl -pe 's/\#\#\# ?//' > generated/walkthrough.txt
	grep '###' ./wicked21st/techtree.py|perl -pe 's/\#\#\# ?//' >> generated/walkthrough.txt
	grep '###' ./wicked21st/project.py|perl -pe 's/\#\#\# ?//' >> generated/walkthrough.txt
	printf "\nGraph\n" >> generated/walkthrough.txt
	python3 ./show_graph.py  >> generated/walkthrough.txt
	printf "\nCascade\n" >> generated/walkthrough.txt
	python3 ./graph_to_cascades.py  >> generated/walkthrough.txt

