def get_py_module(df, save_path):

    import pandas as pd
    import dis
    from collections import defaultdict
    import re
    from itertools import chain

    df.dropna(subset = ['content'], inplace = True)
    df.reset_index(drop = True, inplace = True)

    df['language'] = df['path'].apply(lambda x: str(x).split('/')[-1].split('.')[-1])
    df_python = df[df['language'].isin(['py', 'ipynb'])]
    df_python.reset_index(drop = True, inplace = True)


    df_python['module'] = 0
    df_python['function'] = 0

    for i in range(len(df_python['content'])):
        statements = df_python['content'][i]

        try:

            instructions = dis.get_instructions(statements)
            imports = [__ for __ in instructions if 'IMPORT' in __.opname]

            grouped = defaultdict(list)
            for instr in imports:
                grouped[instr.opname].append(instr.argval)

            df_python['module'][i] = grouped['IMPORT_NAME']
            df_python['function'][i] = grouped['IMPORT_FROM']

        except SyntaxError:

            import_name = []

            code = df_python['content'][i].split('\n')
            r = re.compile(".*import")
            newlist = list(filter(r.match, code)) # Read Note

            # get import
            r = re.compile("import")
            importlist = list(filter(r.match, newlist)) # Read Note
            a = [importlist[i].split("import",1)[1].replace(" ", "").split(',') for i in range(len(importlist))]
            import_name.append(list(chain.from_iterable(a)))
            # get from package
            r = re.compile("from")
            newlist = list(filter(r.match, newlist)) # Read Note
            import_name.append([newlist[i].split("from",1)[1].split(' ')[1] for i in range(len(newlist))])

            a = [newlist[i].split("import",1)[1].split(',') for i in range(len(newlist))]
            a = list(chain.from_iterable(a))
            import_from = [a[i].strip() for i in range(len(a))]

            # if exclude as in function
            for j in range(len(import_from)):
                split = import_from[j].split(' ')
                if len(split)> 1 :
                    import_from[j] = split[0]

            df_python['function'][i] = import_from
            df_python['module'][i] = list(chain.from_iterable(import_name))


        df_python.to_csv(save_path, index = False)

    return df_python


