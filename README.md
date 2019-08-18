
#Reddit Sentiment Analysis Marketing Tool


## Inspiration
It can be very difficult and expensive to find what a certain target market will be interested in, as well as change their ads accordingly. Our group decided to focus on popular social media site Reddit, to try and see what is most popular at the moment. This program can be much cheaper to a company than other market research, as it benefits off social media that people already use.

## What it does
The code will find a sentiment score for specific objects in images to predict which objects have the most positive impact on a photo. This can be used to extrapolate which objects should be included in images to result in a high performing post for marketing strategies.

## How we built it
The program begins by scraping Reddit comments and assigns each post a sentiment value for the comments. After, it will assign the sentiment value for the associated comments to each object in the image. Then it will repeat this for many images and comments and get an average for each of the detected objects, the detection of objects is done using the IBM Watson API.The sentiment of each object is graphed, to see which object has the largest positive impact. We used another algorithm that suggests users what they can add to their own photo in order to improve the positivity based on the sentiment from other objects. Each suggestion takes into context what is already in the photo to provide better results. It was built on Python and uses Indico API as well as Watson IBM for the analysis.

## Challenges we ran into
Both of the APIs had their difficulties when used in a batch situation. We were often kicked out of the Indico API when processing large batches of information and due to the depth of the complexity of the Indico API, the sentimental analysis often took a long time. We would have liked to create some filtering criteria, in order to make this process more efficient if we had more time.