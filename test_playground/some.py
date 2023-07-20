# import traceback
# def first():
#     second()

# def second():
#     limit = 20
#     stack = traceback.extract_stack(limit=limit)
#     print("="*50)
#     print(f"depth: {len(stack)}")
#     for i, f in enumerate(stack):
#         bracket = '╰─'
#         if i < len(stack)-1:
#             bracket = '├─'
#         if i!=0:
#             print('  '*(i-1)+'╰─╮')
#         if i==0:
#             bracket = '╭─'

#         print(f"{'  '*i+bracket}{f.name} at {f.lineno:03d} ({f.line})")
#     print()

# first()
info = {"deviceState":dict(
        keyDownWithoutModifiers=None,
        commandDown=None,
        shiftDown=None,
        optionDown=None,
        controlDown=None,
    )}
print(f'keyDown: {info["deviceState"]["keyDownWithoutModifiers"]} cmd: {info["deviceState"]["commandDown"]} shift: {info["deviceState"]["shiftDown"]} option: {info["deviceState"]["optionDown"]} control: {info["deviceState"]["controlDown"]}')