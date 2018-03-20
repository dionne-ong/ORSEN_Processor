# ORSEN_Processor
The python code for the input processing / output generator for ORSEN (Oral Storytelling Entitiy)

## Dependencies
- PyMySQL
- spaCy
- neural Coref ( https://github.com/huggingface/neuralcoref )

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
