# VocalAIze

## Sections

- [About](#about)
- [Demo](#demo)
- [Command Line Script Setup](#command-line-script-setup)

## About <a id="about"></a>

VocalAIze is a comprehensive web application that combines advanced voice cloning, translation, SMS/email integration, and audio management functionalities in one intuitive platform. Whether you're a language learner, a globetrotting traveler, or a busy professional, our app has something for everyone:

-Voice Cloning and Translation: Instantly clone your voice and translate it into multiple languages with unparalleled accuracy. Break down language barriers and communicate effortlessly with friends, family, and colleagues around the world.

-SMS/Email Integration: Seamlessly send voice messages via SMS or email, adding a personal touch to your digital communications. Express yourself more authentically and convey emotions and nuances that text alone cannot capture.

-Audio Management: Easily save and organize your audio recordings for language learning, professional communication, or personal organization. Keep all your voice notes, memos, and conversations in one convenient location for easy access and reference.

Please note that VocalAIze is no longer being hosted as a web application. It was solely funded by our team and is now available as a command line script. This script allows you to leverage the original voice cloning and translation technology independently, ensuring you can still benefit from our advanced features regardless of the web application’s status.

## WebApp Demo <a id="demo"></a>

https://github.com/RobCaamano/VocalAIze/assets/65639885/087b27ff-a80e-4b21-9a0a-82fe70267eea

## Translation Demo

https://github.com/RobCaamano/VocalAIze/assets/65639885/eac02793-7546-4fc0-9668-e3e2a0731f62

https://github.com/RobCaamano/VocalAIze/assets/65639885/206cd6a6-1a99-4fdf-b2ea-ed7b7f65db9e

## Using CMD Translation Script <a id="command-line-script-setup"></a>

Since VocalAIze is no longer being hosted, I've created a simple command line version with the original voice cloning and translation technology

### How to use:

Before running the script, ensure you have Python installed on your machine. You can download Python from the [official website](https://www.python.org/downloads/).

1. Clone the repository to your local machine

```
git clone https://github.com/RobCaamano/VocalAIze.git
```

3. Download requirements.txt from the translation_cmd directory. It is recommended to do this in a virtual environment. For information about creating and using conda environments, visit their [site](https://conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html).

```
cd '[path to dir]'
pip install -r requirements.txt
```

3. Run the script in your virtual environment

```
python ./translate.py
```

4. Follow the on-screen prompts to select languages

5. Select input audio file from file explorer

The file will be opened upon completion and will be saved to the "saved" folder in the project directory

## Frontend & Backend Repository Links

[Frontend](https://github.com/SaminChowdhury/vocalaize-frontend)

[Backend](https://github.com/SaminChowdhury/vocalaize-backend)
