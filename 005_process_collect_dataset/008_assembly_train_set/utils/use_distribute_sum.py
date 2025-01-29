from distribute_sum import distribute_sum


# Тестирование
list_init = [5700, 46, 1699, 464, 154, 458, 39, 8, 356, 223, 253]
s = 4000

result = distribute_sum(list_init, s)
print(f"Исходный список: {list_init}")
print(f"Новый список   : {result}")
print(f"Сумма нового списка: {sum(result)}")
print(f"Заданная сумма: {s}")