import os
import textwrap
import time


def color(string_name, color_name=None):
    """
    Change text color for the Linux terminal.
    """

    attr = ['1']
    # bold

    if color_name:
        if color_name.lower() == "red":
            attr.append('31')
        elif color_name.lower() == "green":
            attr.append('32')
        elif color_name.lower() == "yellow":
            attr.append('33')
        elif color_name.lower() == "blue":
            attr.append('34')
        return '\x1b[%sm%s\x1b[0m' % (';'.join(attr), string_name)

    else:
        if string_name.strip().startswith("[!]"):
            attr.append('31')
            return '\x1b[%sm%s\x1b[0m' % (';'.join(attr), string_name)
        elif string_name.strip().startswith("[+]"):
            attr.append('32')
            return '\x1b[%sm%s\x1b[0m' % (';'.join(attr), string_name)
        elif string_name.strip().startswith("[*]"):
            attr.append('34')
            return '\x1b[%sm%s\x1b[0m' % (';'.join(attr), string_name)
        elif string_name.strip().startswith("[>]"):
            attr.append('33')
            return '\x1b[%sm%s\x1b[0m' % (';'.join(attr), string_name)
        else:
            return string_name


def title(version, modules, listeners, agents):
    """
    Print the tool title, with version.
    """
    os.system('clear')
    print("================================================================================")
    print(" [Empire]  Post-Exploitation Framework")
    print('================================================================================')
    print(" [Version] %s | [Web] https://github.com/BC-SECURITY/Empire" % version)
    print('================================================================================')
    print(" [Starkiller] Multi-User GUI | [Web] https://github.com/BC-SECURITY/Starkiller")
    print('================================================================================')
    print("""
   _______ .___  ___. .______    __  .______       _______
  |   ____||   \/   | |   _  \  |  | |   _  \     |   ____|
  |  |__   |  \  /  | |  |_)  | |  | |  |_)  |    |  |__
  |   __|  |  |\/|  | |   ___/  |  | |      /     |   __|
  |  |____ |  |  |  | |  |      |  | |  |\  \----.|  |____
  |_______||__|  |__| | _|      |__| | _| `._____||_______|

""")
    print('       ' + color(modules, 'green') + ' modules currently loaded')
    print('')
    print('       ' + color(listeners, 'green') + ' listeners currently active')
    print('')
    print('       ' + color(agents, 'green') + ' agents currently active')
    print('')


def loading():
    """
    Print and ascii loading screen.
    """

    print("""
                              `````````
                         ``````.--::///+
                     ````-+sydmmmNNNNNNN
                   ``./ymmNNNNNNNNNNNNNN
                 ``-ymmNNNNNNNNNNNNNNNNN
               ```ommmmNNNNNNNNNNNNNNNNN
              ``.ydmNNNNNNNNNNNNNNNNNNNN
             ```odmmNNNNNNNNNNNNNNNNNNNN
            ```/hmmmNNNNNNNNNNNNNNNNMNNN
           ````+hmmmNNNNNNNNNNNNNNNNNMMN
          ````..ymmmNNNNNNNNNNNNNNNNNNNN
          ````:.+so+//:---.......----::-
         `````.`````````....----:///++++
        ``````.-/osy+////:::---...-dNNNN
        ````:sdyyydy`         ```:mNNNNM
       ````-hmmdhdmm:`      ``.+hNNNNNNM
       ```.odNNmdmmNNo````.:+yNNNNNNNNNN
       ```-sNNNmdh/dNNhhdNNNNNNNNNNNNNNN
       ```-hNNNmNo::mNNNNNNNNNNNNNNNNNNN
       ```-hNNmdNo--/dNNNNNNNNNNNNNNNNNN
      ````:dNmmdmd-:+NNNNNNNNNNNNNNNNNNm
      ```/hNNmmddmd+mNNNNNNNNNNNNNNds++o
     ``/dNNNNNmmmmmmmNNNNNNNNNNNmdoosydd
     `sNNNNdyydNNNNmmmmmmNNNNNmyoymNNNNN
     :NNmmmdso++dNNNNmmNNNNNdhymNNNNNNNN
     -NmdmmNNdsyohNNNNmmNNNNNNNNNNNNNNNN
     `sdhmmNNNNdyhdNNNNNNNNNNNNNNNNNNNNN
       /yhmNNmmNNNNNNNNNNNNNNNNNNNNNNmhh
        `+yhmmNNNNNNNNNNNNNNNNNNNNNNmh+:
          `./dmmmmNNNNNNNNNNNNNNNNmmd.
            `ommmmmNNNNNNNmNmNNNNmmd:
             :dmmmmNNNNNmh../oyhhhy:
             `sdmmmmNNNmmh/++-.+oh.
              `/dmmmmmmmmdo-:/ossd:
                `/ohhdmmmmmmdddddmh/
                   `-/osyhdddddhyo:
                        ``.----.`

                Welcome to the Empire""")
    time.sleep(3)
    os.system('clear')


def text_wrap(text, width=35):
    """
    Wraps text to newlines given a maximum width per line.
    :param text:
    :param width:
    :return: String wrapped by newlines at the given width
    """
    return '\n'.join(textwrap.wrap(str(text), width=width))


def display_module(module_name, module):
    print(color('\n{0: >20}'.format("Name: "), 'blue') + str(module_name.split('/')[-1]))
    print(color('{0: >20}'.format("Module: "), 'blue') + str(module['Name']))
    if 'NeedsAdmin' in module:
        print(color('{0: >20}'.format("NeedsAdmin: "), 'blue') + ("True" if module['NeedsAdmin'] else "False"))
    if 'OpsecSafe' in module:
        print(color('{0: >20}'.format("OpsecSafe: "), 'blue') + ("True" if module['OpsecSafe'] else "False"))
    if 'Language' in module:
        print(color('{0: >20}'.format("Language: "), 'blue') + str(module['Language']))
    if 'MinLanguageVersion' in module:
        print(color('{0: >20}'.format("MinLanguageVersion: "), 'blue') + str(module['MinLanguageVersion']))
    if 'Background' in module:
        print(color('{0: >20}'.format("Background: "), 'blue') + ("True" if module['Background'] else "False"))
    if 'OutputExtension' in module:
        print(color('{0: >20}'.format("OutputExtension: "), 'blue') + (
            str(module['OutputExtension']) if module['OutputExtension'] else "None"))

    if module['Techniques']:
        print(color("\nMITRE ATT&CK Techniques:", 'blue'))
        for techniques in module['Techniques']:
            print("  https://attack.mitre.org/techniques/" + techniques)

    if module['Software']:
        print(color("\nMITRE ATT&CK Software:", 'blue'))
        print("  https://attack.mitre.org/software/" + module['Software'])

    print(color("\nAuthors:", 'blue'))
    for author in module['Author']:
        print("  " + author)

    print(color("\nDescription:", 'blue'))
    desc = wrap_string(module['Description'], width=60, indent=2, indentAll=True)
    if len(desc.splitlines()) == 1:
        print("  " + str(desc))
    else:
        print(desc)

    if 'Comments' in module:
        comments = module['Comments']
        if isinstance(comments, list):
            comments = ' '.join(comments)
        if comments.strip() != '':
            print(color("\nComments:", 'blue'))
            if isinstance(comments, list):
                comments = ' '.join(comments)
            comment = wrap_string(comments, width=60, indent=2, indentAll=True)
            if len(comment.splitlines()) == 1:
                print("  " + str(comment))
            else:
                print(comment)
    print("\n")


def wrap_string(data, width, indent, indentAll=False, followingHeader=None):
    """
    Print a option description message in a nicely
    wrapped and formatted paragraph.

    followingHeader -> text that also goes on the first line
    """

    data = str(data)

    if len(data) > width:
        lines = textwrap.wrap(textwrap.dedent(data).strip(), width=width)

        if indentAll:
            returnString = ' ' * indent + lines[0]
            if followingHeader:
                returnString += " " + followingHeader
        else:
            returnString = lines[0]
            if followingHeader:
                returnString += " " + followingHeader
        i = 1
        while i < len(lines):
            returnString += "\n" + ' ' * indent + (lines[i]).strip()
            i += 1
        return returnString
    else:
        return data.strip()


def display_stager(stager):
    """
    Displays a stager's information structure.
    """

    print(color("\nName: ", 'blue') + stager['Name'])

    print(color("\nAuthors:", 'blue'))
    for author in stager['Author']:
        print("  " + author)

    print(color("\nDescription:", 'blue'))
    desc = wrap_string(stager['Description'], width=50, indent=2, indentAll=True)
    if len(desc.splitlines()) == 1:
        print("  " + str(desc))
    else:
        print(desc)

    if 'Comments' in stager['Comments']:
        comments = stager['Comments']
        if isinstance(comments, list):
            comments = ' '.join(comments)
        if comments.strip() != '':
            print(color("\nComments:", 'blue'))
            if isinstance(comments, list):
                comments = ' '.join(comments)
            comment = wrap_string(comments, width=60, indent=2, indentAll=True)
            if len(comment.splitlines()) == 1:
                print("  " + str(comment))
            else:
                print(comment)

    print("\n")

