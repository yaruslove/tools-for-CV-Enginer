

def distribute_sum(list_init, amount_in_class):
   n = len(list_init)
   list_new = [0] * n
   
   # Шаг 1: Находим маленькие элементы (≤ amount_in_class/n)
   threshold = amount_in_class / n
   small_indices = [i for i, x in enumerate(list_init) if x <= threshold]
   
   # Копируем маленькие элементы в новый список
   remaining_sum = amount_in_class
   for i in small_indices:
       list_new[i] = list_init[i]
       remaining_sum -= list_init[i]
   
   # Находим индексы элементов для распределения
   distribute_indices = [i for i in range(n) if i not in small_indices]
   
   if distribute_indices:  # Если есть элементы для распределения
       # Начальное равномерное распределение
       equal_share = remaining_sum / len(distribute_indices)
       
       # Распределяем, учитывая ограничения исходного списка
       while True:
           over_limit = []  # Элементы, превышающие лимит
           under_limit = [] # Элементы с запасом
           
           # Проверяем каждый элемент
           for i in distribute_indices:
               if equal_share > list_init[i]:
                   over_limit.append(i)
               else:
                   under_limit.append(i)
                   
           if not over_limit:  # Если нет превышений
               break
               
           # Фиксируем превышающие элементы
           extra_sum = 0
           for i in over_limit:
               list_new[i] = list_init[i]
               extra_sum += equal_share - list_init[i]
               distribute_indices.remove(i)
               
           if distribute_indices:  # Если остались элементы для распределения
               equal_share += extra_sum / len(distribute_indices)
           else:
               break
       
       # Записываем финальные значения c округлением
       for i in distribute_indices:
           list_new[i] = round(min(equal_share, list_init[i]))
           
   # Финальное округление всех элементов
   list_new = [round(x) for x in list_new]
   
   return list_new


# def distribute_sum(list_init, s):
#     n = len(list_init)
#     list_new = [0] * n
    
#     # Шаг 1: Находим маленькие элементы (≤ s/n)
#     threshold = s / n
#     small_indices = [i for i, x in enumerate(list_init) if x <= threshold]
    
#     # Копируем маленькие элементы в новый список
#     remaining_sum = s
#     for i in small_indices:
#         list_new[i] = list_init[i]
#         remaining_sum -= list_init[i]
    
#     # Находим индексы элементов для распределения
#     distribute_indices = [i for i in range(n) if i not in small_indices]
    
#     if distribute_indices:  # Если есть элементы для распределения
#         # Начальное равномерное распределение
#         equal_share = remaining_sum / len(distribute_indices)
        
#         # Распределяем, учитывая ограничения исходного списка
#         while True:
#             over_limit = []  # Элементы, превышающие лимит
#             under_limit = [] # Элементы с запасом
            
#             # Проверяем каждый элемент
#             for i in distribute_indices:
#                 if equal_share > list_init[i]:
#                     over_limit.append(i)
#                 else:
#                     under_limit.append(i)
                    
#             if not over_limit:  # Если нет превышений
#                 break
                
#             # Фиксируем превышающие элементы
#             extra_sum = 0
#             for i in over_limit:
#                 list_new[i] = list_init[i]
#                 extra_sum += equal_share - list_init[i]
#                 distribute_indices.remove(i)
                
#             if distribute_indices:  # Если остались элементы для распределения
#                 equal_share += extra_sum / len(distribute_indices)
#             else:
#                 break
        
#         # Записываем финальные значения c округлением
#         for i in distribute_indices:
#             list_new[i] = round(min(equal_share, list_init[i]))
            
#     # Финальное округление всех элементов
#     list_new = [round(x) for x in list_new]
    
#     return list_new

