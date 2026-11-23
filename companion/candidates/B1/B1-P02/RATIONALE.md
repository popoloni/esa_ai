# Proposal B1-P02

The implementation uses a familiar numeric representation and checks finiteness explicitly before choosing a queue. Its result fields and ordinary boundary examples agree with the current interface. This keeps the parser and comparison compact. I would review the conversion boundary together with the admitted input language, especially where two different source strings can map to the same stored numeric value.
