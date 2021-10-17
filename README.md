Project developed by Manuel Salvador and Daniel Sabag as part as Intelligent Systems subject.

This desktop app is able to reproduce a video that the user chooses and from that video it will take out the audio and convert it into .wav file, then it will translate the sound from the video to text. With this text we are able to apply different codes in relation to different actions that a driver does while in the car.

This project is based around stops signs and how the driver interacts with the car and with the other cars on the road. If you check the final test video (link in the videos.txt file), you will see me driving and talking about what am i doing, like down shifting (gear down), look left or right, brake, push clutch pedal etc. All of this are different actions that the driver usually does but they do almost without thinking, with this activity we tried to detect all this actions and apply different codes for each action the driver does.


This "codes" can be applied by clicking the button on the bootom left corner that says "Sugerir codigos". This will rerun the proccess of analizing the text and trying to find new codes. Whenever it does it will print the code next to the command said. 

When ever the user wants, he can modify the text shown in screen so he can correct any mistakes the translator do.
![imagen](https://user-images.githubusercontent.com/27558633/137604918-007f9d50-6684-4dda-aed0-8ec74a6e992c.png)

With all of this we give the user the ability to save the transcripted text, to see and colect data on how people interact in the car and how well or bad the app is proccessing the videos that people import.

In the image (png) you can see the route i took while driving. This will help you understand all the stops signs 



To be able to run the code you will need the follow up software:
K-Lite Codec -> Video player used in the app.
http://www.codecguide.com/configuration_tips.htm?version=1610

We recommend you run the code in Visual Studio where you will be able to see the progress on how we extract the audio, the conversion and how we transcript it using google services.

If you have any problems or doubts contact me in my email: manusalvadorg@gmail.com
