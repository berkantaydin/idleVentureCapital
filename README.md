idleVentureCapital
==================

Cross platform idleVenture game clone


Run case like Android
==================
python main.py -m screen:note2,portrait,scale=.60


Close with all threads an app on Linux
==================
ps -ef | grep "main.py" | grep -v grep | awk '{print $2}' | xargs kill -9

