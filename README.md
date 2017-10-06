# WikiChatbot

A simple Telegram chatbot using knowledge base which had been crowdsourced from Wikipedia pages.

## How to use
First, connect to  [Chatbot](http://t.me/nlpproject_bot)

Because server might be suspended when there is no incoming request for a period time, the first response will be delayed about 1 minute for resuming the server again.

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
	
	```
	Big
	```
	
	or if Users don't have any answer
	
	```
	No
	```
    
    
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
    
### Conversation example

	- Hello !

	+ Hello, what would you like to talk about ?

	- Computing

	+ Would you like to ask a question ?

	- no

	+ What is the group of Motorola EM28/EM330 ?

	- Mobile device

	+ Thank you ! I got your answer !



### Note

Because of large size, pretrained model for relation detection and local database were not kept in github repo but google drive for references: https://goo.gl/jnAmtw

## Authors

**Nguyen Minh Gia Huy** - Sapienza University of Rome

Natural Language Processing Course.
