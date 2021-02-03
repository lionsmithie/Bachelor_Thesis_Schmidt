## Guidance zur Evaluierung:

Dieser Teil der Evaluierung dient dazu, zu prüfen, ob die für die CF Rollen Agent/Theme automatisch identifizierten
 Frame Elements tatsächlich der Rolle des Agents/Themes entsprechen.
 In den meisten Fällen ist das mit ja/nein zu beantworten.
 Sollte sich in einem Satz kein Agent oder kein Theme befindend, bitte ebenfalls angeben (Erklärung folgt).


Die Evaluierung wird nach jedem vollständig (!) annotierten Verb zwischengespeichert.


## Durchführung: 

Zuerst muss der eigene Username eingeben werden. Das dient dazu, die Evaluierung zwischenzuspeichern.
Am besten also den eigenen Namen nehmen, den kann man nicht vergessen.
Alternativ kann man sonst auch im Ordner ``Evaluation/eval`` nachsehen.

Insgesamt werden 25 Verben evaluiert. Für jedes Verb werden zwei Sätze nacheinander angezeigt, die zu evaluieren sind.
Über jedem Satz steht noch einmal das Verb, um welches es sich in diesem Satz handelt.
Wichtig: Da in vielen Sätzen mehrere Verben vorkommen, bitte immer rückversichern,
dass das korrekte Verb betrachtet wird.

In Bezug auf dieses Verb soll geprüft werden, ob die für Agent/Theme gefundenen Rollen korrekt sind oder falsch.
Der selbe Satz wird immer zwei Mal angezeigt. Beim ersten Mal geht es immer um den Agent,
beim zweiten Mal immer um das Theme.
Weiter unten wird ein Beispiel durchgegangen und kommentiert.  


### Agent
Für die Rolle des Agents ist wichtig, sich zu fragen: WER oder WAS führt die Aktion aus;
WER oder WAS ist Akteur oder Protagonist?  
Wichtig: Es gibt auch Sätze, bei denen es sich um ein Verb im Passiv handelt:

Beispiel: "He was killed by the police."  
In diesem Fall ist der Agent "the police" und NICHT "he".  
-> Wer oder Was führt die Aktion aus;
Wer oder Was killt? -> "the police".

Es kann sein, dass der Algorithmus den Agent in solch einem Fall nicht als "the police",
sondern als "by the police" erkennt.
Das ist als korrekt zu klassifizieren, da dies an der FrameNet-Annotation liegt.
Auch in FrameNet ist dann diese Rolle mit "by the police" besetzt.
Diese "Regel" gilt generell. Falls nach eigenem Empfinden der Agent an sich stimmt,
aber man mit der exakten Phrasenlänge nicht zufrieden ist,
bitte den Agent dennoch als korrekt markieren, da diese Fälle immer auf die FrameNet-Annotation zurückzuführen sind.  


### Theme
Für die Rolle des Themes ist wichtig, sich zu fragen: WER oder WAS wird direkt von einer Aktion beeinflusst,
ist ein direkter Outcome oder hat einen direkten semantischen Bezug zur Aktion?

Beispiel: "I felt that something was wrong."  
-> "that something was wrong" ist ein direkter Outcome der Aktion "feel",
es entspricht also dem Theme.  
Wichtig: Für Passivsätze gilt hier ebenfalls Vorsicht. Obiges Beispiel:
"He was killed by the police." -> "He" ist direkt von der Aktion "kill" beeinflusst,
"he" ist also das Theme und nicht der Agent.


## Wie soll genau evaluiert werden?
Für jeden Satz wird das (für den Agent oder das Theme) gefundene Frame Element (Die semantische Rolle in FrameNet;
sowas wie "Speaker", "Experiencer", aber kann auch zufälligerweise "Agent" heißen) angezeigt.
Ebenfalls wird das Textfragment, auf das diese Rolle veweist, angezeigt:

Beispiel: "He was killed by the police."  
Für den Agent würde dann ein Ergebnis kommen wie:  
Violator  -->  "by the police"

[Die Rolle des Violators ist zu Demonstrationszwecken frei erfunden]

Wie oben bereits erläutert, entspricht "by the police" der Rolle des Agents.
Der Name des Frame Elements kann übrigens auch helfen, kann aber auch ignoriert werden.
Wenn man sich das Verb in einem einfachen, nicht passivischem Satz vorstellt, beispielsweise "She kills the fly.",
so wird eindeutig, dass die Rolle des Agents wohl der Rolle des "Violators" entspricht.

An dieser Stelle muss der User entscheiden,
ob das gefundene Frame Element/das Textfragment also auf die Rolle des Agents/Themes passt:


* Für Ja -> 'y' eingeben
* Für Nein -> 'n' eingeben
* '-' engeben falls es in dem jeweiligen Satz keinen Agent/Theme für das vorgegebene Verb gibt,
obwohl eines angezeigt wird (Beispiel folgt)
* bei Unsicherheit -> '?' eingeben  


### Beispiel für einen fehlenden Agent
Verb: kill

"The battle came to an end, the knights tortured those who fell on the ground and at least 100 men were killed."  
Violator --> "the knights"

Hier könnte man geneigt, sein, den Agent mit "the knights" als korrekt zu klassifizieren. Das wäre falsch.
Das Verb, um das es sich handelt, ist "kill". Wir wissen nur, dass "at least 100 men" getötet wurden,
aber nirgendwo wird explizit erwähnt, Wer oder Was diese Aktion ausgeführt hat. In diesem Fall bitte mit '-' antworten,
da kein Agent für das Verb vorhanden ist, obwohl ein Frame Element angezeigt wurde.



Nun ein Beispiel, wie es letztlich aussieht:  

###-------------------------AGENT------------------------  
The sentence to be evaluated (VERB: CRACK):
We 'd have cracked somebody 's head if we 'd used them .

For the role of the Agent, the following Frame Element(s) have been found:  
Agent -> 'We'

Does at least one of the found Frame Elements match the Role of the Agent?  
y/n/-/?:  


* In diesem Fall simmt die Rolle des Agents mit "we" überein. Es kann also mit ja -> y geantwortet werden.  
Es geht mit dem Theme weiter:

  
###-------------------------THEME------------------------

The sentence to be evaluated (VERB: CRACK):  
We 'd have cracked somebody 's head if we 'd used them .  

For the role of the Theme, the following Frame Element(s) have been found:  
Body_part -> 'somebody 's head'

Does at least one of the found Frame Elements match the Role of the Theme?  
y/n/-/?:  

* Auch in diesem Fall stimmt die Rolle. In einem späteren Satz hingegen stimmt die Rolle des Themes nicht:  

###-------------------------THEME------------------------

The sentence to be evaluated (VERB: CRACK):  
Worriedly judging her moment , and hoping fervently that the other two heard nothing ,
she slipped out behind the third man , and cracked him over the head with the cutters .  

For the role of the Theme, the following Frame Element(s) have been found:  
Body_part -> 'over the head'  

Does at least one of the found Frame Elements match the Role of the Theme?  
y/n/-/?:  


* Hier wäre das korrekte Frame Element für das Theme "him". Also bitte mit nein antworten. 


---------
----------
Es soll jetzt geprüft werden, wie akkurat die Konnotationen sind, allerdings nicht so, dass man entscheiden soll, ob der Wert der Konnotation stimmt, sondern indem man selbst eine Konnotation eingibt. 

Die einzugebenden Werte reichen von
-2 negativ
-1 leicht negativ
0 neutral
1 leicht positiv
2 positiv
? Keine Konnotation vorhanden

Keine Konnotation vorhanden heißt, dass es deiner Meinung nach hier kein Sentiment gibt oder geben kann. 

Z.B. "She hates rainy days." 
Perspective(Agent->Theme): Perspektive von ihr gegenüber den verregneten Tagen: Würde ich als negativ einstufen, also 2

Perspective(Theme->Agent): Hier gibt es keine Konnotation, weil rainy days keine Person ist bzw keine Entität. Hier dann bitte mit ? antworten

Die Bewertung läuft so, dass du immer zuerst das Verb ohne Satzkontext bekommst und (bewusst) ohne Kontext die 5 folgenden Features einstufen sollst von -2 bis 2, oder '?':
Perspective(Writer->Agent)
Perspective(Writer->Theme)
Perspective(Agent->Theme)
Perspective(Theme->Agent)
Value(Theme)

Gehe bei dem Verb ohne Kontext bitte davon aus, dass der Writer weder Agent noch Theme ist. 

Anschließend kommen für das jeweilige Verb noch zwei Beispielsätze (sind die gleichen wie auch bei der anderen eval), für die du dann jeweils auch nochmal dieselben Features bewerten sollst. Falls die Sätze hier aus einer Ich-Perspektive geschrieben sind und somit der Writer entweder Agent oder Theme ist, dann bitte trotzdem akkurat bewerten, sprich, wenn der Writer = Agent ist, dann wäre 
Perspective(Writer->Agent) = 2;
Perspective(Agent->Theme) = Perspective(Writer->Theme) etc.

Bei Value(Theme) handelt es sich um den Wert, den der Autor dem Theme zuschreibt. 

Wenn du merkst, dass du das Verb ohne Kontext ganz anders gelesen hast und die Konnotation, die du dort eingegeben hast, jetzt bei den Sätzen nicht mehr passt, dann NICHT nochmal machen. Genau darum gehts nämlich, dass das teilweise ohne Kontext keinen Sinn macht bzw was anderes vermittelt. Also das wäre sogar dann für meine BA eher gut :)