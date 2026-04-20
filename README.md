setup
1a. mac ->python3 -m venv venv
1b. windows -> python -m venv venv
2a. mac -> source venv/bin/activate
2b. windows -> venv\Scripts\activate.bat
3. pip install -r requirements.txt
3a. pip install -U python-jobspy (version issue?)
4. test ollama if installed model -> ollama run llama3.2

ideal flow
linkedin + google sheet base runs -> enrichment_run -> gap_and_opp_screen -> output to matched_master -> dashboard