class Queue():
    def __init__(self,array =[] ):
        self.array = array

    def length(self):
        if not self.array:
            return 0
        else:
            return len(self.array)

    def is_Empty(self):
        return len(self.array) == 0

    def push(self, value):
        self.array.append(value)
        return

    def pop(self):
        self.array.pop(0)
        return
    def top(self):
        return self.array[0]

    def travel(self):
        print(self.array)
