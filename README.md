# WikiChatbot

A simple Telegram chatbot using knowledge base which had been crowdsourced from Wikipedia pages.

## How to use
First, connect to  [Chatbot](http://t.me/nlpproject_bot)

Because server might be suspended when there is no incoming request for a period time, the first message will be delayed about 30 seconds for resuming the server again.

A conversation with chatbot includes 4 steps:
* Step 1: Chatbot will ask a specific domain
  
    ```
    Hello, which field should we need to discuss ?
    ```
    User has to give a response in one of 34 domain names of Wikipedia or "Unknown" if want to specify an general domain.
    ```
    Animals
    Art, architecture, and archaeology
    Biology
    Business, economics, and finance
    Chemistry and mineralogy
    Computing
    Culture and society
    Education
    Engineering and technology
    Farming
    Food and drink
    Games and video games
    Geography and places
    Geology and geophysics
    Health and medicine
    Heraldry, honors, and vexillology
    History
    Language and linguistics
    Law and crime
    Literature and theatre
    Mathematics
    Media
    Meteorology
    Music
    Numismatics and currencies
    Philosophy and psychology
    Physics and astronomy
    Politics and government
    Religion, mysticism and mythology
    Royalty and nobility
    Sport and recreation
    Textile and clothing
    Transport and travel
    Warfare and defense
    ```
    
    To support for spelling mistakes, user's domain input could be different from target domains maximum 2 characters by Leveshtein string distance. All the responses of user in conversation are case ignored.

* Step 2: Chatbot will ask if users want to ask or receive a question.

    ```
    Would you like to ask a question ?
    ```
    
    Users have 2 options to answer: "Yes" or "No" that each corresponds to "Querying" and "Enriching" options.

#### Querying
* Step 3: Chatbot will tell users to give a question

    ```
    What is your question ?
    ```

    Users then have to give a question in one of 2 types: Normal question or Yes/No question.

    ```
    What is a computer ?
    ```

    ```
    Is Italy in Southern Europe ?
  ```
  
* Step 4: Chatbot will give the answer to user
  
    ```
    Device
    ```
    
    or 
    
    ```
    Yes
    ```
    
    or if Chatbot doesn't know the answer
    
    ```
    I don't know the answer.
    ```
    
    Conversation ends. 
    User can start a new session of conversation by typing anything.

#### Enriching
* Step 3: Chatbot will ask users a question  
      
    ```
    What is the size of Preludes ?
    ```
    
    Jormal normal questions will be asked. 
		Users then have to answer the question.
    
    
* Step 4: Chatbot will tell users to end conversation
    
    If users give an answer

    ```
    I got your answer ! Thank you !
    ```
    
    Or if users don't have any answer

    ```
    Don't worry ! You will can answer it next time.
    ```
    
    Conversation ends. 
    User can start a new session of conversation by typing anything.
    
### Prerequisites

What things you need to install the software and how to install them

```
Give examples
```

### Installing

A step by step series of examples that tell you have to get a development env running

Say what the step will be

```
Give the example
```

And repeat

```
until finished
```

End with an example of getting some data out of the system or using it for a little demo

## Running the tests

Explain how to run the automated tests for this system

### Break down into end to end tests

Explain what these tests test and why

```
Give an example
```

### And coding style tests

Explain what these tests test and why

```
Give an example
```

## Deployment

Add additional notes about how to deploy this on a live system

## Built With

* [Dropwizard](http://www.dropwizard.io/1.0.2/docs/) - The web framework used
* [Maven](https://maven.apache.org/) - Dependency Management
* [ROME](https://rometools.github.io/rome/) - Used to generate RSS Feeds

## Contributing

Please read [CONTRIBUTING.md](https://gist.github.com/PurpleBooth/b24679402957c63ec426) for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/your/project/tags). 

## Authors

* **Billie Thompson** - *Initial work* - [PurpleBooth](https://github.com/PurpleBooth)

See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Hat tip to anyone who's code was used
* Inspiration
* etc
