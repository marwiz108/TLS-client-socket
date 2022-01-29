all:
	ln -s client.py client
	chmod +x client

clean:
	rm client
	rm -rf __pycache__