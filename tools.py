# useful tools
# Derek Fujimoto
# Nov 2024

def prettyprint(fn_equation, *parnames):
    """Function decorator which allows it to have a print function. This takes as
    argument the list of parameters and their errors and prints nicely the fit result
    for use in matplotlib (latex is rendered)

    Args:
        fn_equation (str): latex-rendered string of the equation used in the function
        parnames (str): parameter names
    """
    def wrapper(fn):
        def print(par, std):
            text = [f'Function: {fn_equation}']
            for i, name in enumerate(parnames):
                text.append(f'{name}: {par[i]:.5g} $\pm$ {std[i]:.5g}')
            return '\n'.join(text)
        fn.print = print
        fn.name = fn_equation
        return fn
    return wrapper
