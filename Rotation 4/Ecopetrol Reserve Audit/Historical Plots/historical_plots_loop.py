import historical_plots as hp

# list of fields
fieldList = [('CARACARA',True),
  ('ELIZITA',False),
  ('PEGUITA SOUTH WEST',False),
  ('PEGUITA',True),
  ('RANCHO QUEMADO',False),
  ('REDONDO',False),
  ('TONINA',False),
  ('TORO SENTADO WEST',False),
  ('TORO SENTADO',True),
  ('UNUMA',False)
  ]

# loop to generate plots
for fieldTuple in fieldList:
    field = fieldTuple[0]
    isInj = fieldTuple[1]
    hp.CreateHistoryPlot(field, isInj)
