def option_schema(option) -> dict:
   return {
       "option": option
   }


def options_schema(options) -> dict:
   return [option_schema(option) for option in options]
