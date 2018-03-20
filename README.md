# ORSEN_Processor
The python code for the input processing / output generator for ORSEN (Oral Storytelling Entitiy)

## Dependencies
- PyMySQL
- spaCy
- neural Coref ( https://github.com/huggingface/neuralcoref )
  - Changes
    - data.py : line 338 
        ```
        with open(name + "_vocabulary.txt", encoding="utf8") as f:
        ```
    - algorithm.py : after line 331
        ```
        \
        mention.mention_type == MENTION_TYPE["LIST"]: #EDITED: added List to show They/Them pronouns
        ```

## Modules
- Text Understanding
  - Preprocessing ( DONE )
  - Character Extraction ( 90% )
    - Passive voice, after prepostition
  - Character Detail Extraction ( DONE )
  - Setting Detail Extraction ( 85% )
  - Event Extraction ( TO-REDO )
  
- Dialogue Manager
  - Dialogue Planner
  - Content Determination
  - Sentence Planning
  - Linguistic Realization

- Story Generation
