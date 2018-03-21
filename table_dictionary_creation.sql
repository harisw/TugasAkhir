create table dictionary (
    id int NOT NULL AUTO_INCREMENT,
    word varchar(100) NOT NULL,
    joy_occurences int,
    fear_occurences int,
    anger_occurences int,
    sadness_occurences int,
    disgust_occurences int,
    shame_occurences int,
    guilt_occurences int,
    joy_probs int,
    fear_probs int,
    anger_probs int,
    sadness_probs int,
    disgust_probs int,
    shame_probs int,
    guilt_probs int,
    PRIMARY KEY(id)
);