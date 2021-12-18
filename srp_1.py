import hashlib
import random
import primesieve
from math import gcd
from random import choice
from string import ascii_uppercase

#тест Миллера-Рабина на простоту (False - составное, True - простое)
def Miller_Rabin(n, k=1):
    
    if n == 2 or n == 3:
        return True
    if n % 2 == 0:
        return False
    r = n - 1
    s = 0
    while r % 2 == 0:
        r //= 2
        s += 1
    for i in range(k):
        a = random.randint(2, n - 2)
        x = pow(a, r, n)
        if x == 1 or x == n - 1:
            continue
        for j in range(s - 1):
            x = pow(x, 2, n)
            if x == 1:
                break
        else:
            return False
    return True


def MR_print(num):
    if Miller_Rabin(num):
        return (' - простое')
    else:
        return (' - составное')


# генератор по модулю N
def generator_module(N_input):
    original_set = set()
    current_set = set()
    for num in range(1, N_input):
        if gcd(num, N_input) == 1:
            original_set.add(num)
    # print(f'{initial_set = }')
    for g in range(1, N_input):
        for powers in range(1, N_input):
            current_set.add(pow(g, powers) % N_input)
        # print(f'{current_set = }')
        if original_set == current_set:
            return g


def SRP():
    pswrd = "pswrd123"
    login = "mzabolotskiy"
    N = 0
    k = 3

    print("\nФАКТОРЫ ПРОТОКОЛА: \n")
    #подбор простых чисел q и N = 2 * q + 1
    while not Miller_Rabin(N, 1):
        q = primesieve.nth_prime(random.randint(100, 2000))
        N = 2 * q + 1
        print(f'\tПростое число {q = }\n\tБезопасное простое число 2 * q + 1 = {N = }\t {MR_print(N)}\n')

    #g - генератор по mod N: для любого 0 < X < N существует единственный x такой, что g^x mod N = X")
    g = generator_module(N)
    print(f'\tГенератор по модулю N -> {g = }')

    #k - множитель (может быть хеш-функцией), для простоты и производительности примем его за константу = 3")
    print(f'\tПараметр - множитель в SRP-6 -> {k = }')

    print("\nРЕГИСТРАЦИЯ\n")
    print("\tКлиент вычисляет следующее:")

    #salt - соль, случайная строка"
    salt = ''.join(choice(ascii_uppercase) for i in range(12))
    print(f'\tСлучайная строка: {salt = }')
    
    #x = H(S, p)"
    x = int(hashlib.sha512(salt.encode() + pswrd.encode()).hexdigest(), 16)
    print(f'\tЗашифрованное значение H(S, p) -> {x = }')

    #pswrd - пароль клиента"
    print(f'\t{pswrd = }')

    #v = g^x mod N"
    v = pow(g, x, N)
    print(f'\tВерификатор пароля g^x % N: {v = }')

    print("\nАУТЕНТИФИКАЦИЯ\n")
    print("\tКлиент отправляет на сервер A(вычисленное значение) и I(login):")
    print(f'\t{login = }')

    a = random.randint(2, 100)
    print(f'\tРандомное значение {a = }')

    A = pow(g, a, N)
    print(f'\tЗначение (g^a % N): {A = }')

    print("\tСервер должен убедиться, что A != 0\n")
    
    if A != 0:
        print("\tСервер генерирует случайное число b и вычисляет B = (k*v + g^b % N) % N")

        b = random.randint(2, 100)
        print(f'\tСлучайное число {b = }')

        B = (k * v + pow(g, b, N)) % N
        print(f'\tЗначение (k*v + g^b % N): {B = }')

        print("\tЗатем сервер отсылает клиенту s (соль) и вычисленное значение B")

        print("\tКлиент проверяет, что B != 0\n")
        
        if B != 0:
            print("\tОбе стороны вычисляют скремблер u = H(A, B)")

            u = int(hashlib.sha512(str(A).encode() + str(B).encode()).hexdigest(), 16)
            print(f'\tСкремблер {u = }')

            print("\tЕсли u = 0 -> соединение прерывается\n")
            
            if u != 0:
                print("\tКлиент и сервер вычисляют значение S и общий ключ сессии(K)")
                s_client = pow((B - k*(pow(g, x, N))), (a + u * x), N)
                print(f'\tЗначение S клиента = ((B - k*(g^x % N)) ^ (a + u*x)) % N: {s_client = }')

                k_client = int(hashlib.sha512(str(s_client).encode()).hexdigest(), 16)
                print(f'\tОбщий ключ сессии К со стороны клиента = H(S): {k_client = }\n')

                s_server = pow(A * pow(v, u, N), b, N)
                print(f'\tЗначение S сервера = ((A*(v^u % N)) ^ b) % N: {s_server = }')

                k_server = int(hashlib.sha512(str(s_server).encode()).hexdigest(), 16)
                print(f'\tОбщий ключ сессии К со стороны сервера = H(S): {k_server = }\n')

                if k_server == k_client:
                    print("\t\tУСПЕШНО!\tК клиента = К сервера!\n")
                    print("\tПосле этого сервер и клиент - оба имеют одинаковые К.")
                    print("\nГЕНЕРАЦИЯ ПОДТВЕРЖДЕНИЯ\n")
                    print("\tСервер и клиент вычисляют М")
                    #шифрование значений N,g, I
                    Hash_N = int(hashlib.sha512(str(N).encode()).hexdigest(), 16)
                    Hash_g = int(hashlib.sha512(str(g).encode()).hexdigest(), 16)
                    Hash_I = int(hashlib.sha512(str(login).encode()).hexdigest(), 16)

                    M_client = int(hashlib.sha512(str(Hash_N ^ Hash_g).encode() + str(Hash_I).encode() + str(s_client).encode() + str(A).encode() + str(B).encode() + str(k).encode()).hexdigest(), 16)
                    print(f'\tЗначение M = H( H(N) XOR H(g), H(I), s, A, B, K) со стороны клиента: {M_client = }')
                    M_server = int(hashlib.sha512(str(Hash_N ^ Hash_g).encode() + str(Hash_I).encode() + str(s_server).encode() + str(A).encode() + str(B).encode() + str(k).encode()).hexdigest(), 16)
                    print(f'\tЗначение M = H( H(N) XOR H(g), H(I), s, A, B, K) со стороны сервера: {M_server = }\n')                    
                    if M_client == M_server:
                        print("\tУСПЕШНО!\tM клиента = M сервера\n")
                        print("\tКлиент и сервер вычисляют R")
                        R_client = int(hashlib.sha512(str(A).encode() + str(M_client).encode() + str(k_client).encode()).hexdigest(), 16)
                        print(f'\tЗначение M = H( A, M, K ) со стороны клиента: {R_client = }')
                        R_server = int(hashlib.sha512(str(A).encode() + str(M_server).encode() + str(k_server).encode()).hexdigest(), 16)
                        print(f'\tЗначение M = H( A, M, K ) со стороны сервера: {R_server = }\n')
                        
                        if R_client == R_server:
                            print("\t\tУСПЕШНО!\tR клиента = R сервера")
                            
                        else:
                            print("\t\t ОШИБКА: R клиента != R сервера")
                    else:
                        print("\t\t ОШИБКА: M клиента != M сервера")
                else:
                    print("\t\ОШИБКА!: К клиента != К сервера\n")

                print("\tЕсли вычисленная клиентом R = R c сервера, то подтверждение успешно.")
            else:
                print(" ОШИБКА: u = 0!")
        else:
            print(" ОШИБКА: B = 0")
    else:
        print(" ОШИБКА: A = 0")


if __name__ == "__main__":
    SRP()
