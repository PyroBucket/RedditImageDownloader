# RedditImageDownloader
FastAPI app that allows user to fetch random image from a subreddit and access history of previously downloaded images.
Database file is created at first launch
#How to run:
1. Copy project to your local machine
2. Substitute variables in config.json file with valid creditentials
3. Move your CWD to main folder of the project
4. Build docker image using 
    >docker build -t imagedownloaderimage .
5. Run docker image using 
    >docker run -d --name mycontainer -p 80:80 imagedownloaderimage
6. Once docker is up and running go to localhost/docs to access documentation and start using the app
