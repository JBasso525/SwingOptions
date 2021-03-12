import matplotlib.pyplot as plt

def get_underlying(periods, u, chg):
    underlying = {}

    for j in range(periods+1):
        underlying[j] = []

        for i in range(j+1):
            price_u = u * (chg ** (j - i)) / (chg ** i)
            underlying[j].append(price_u)

    return underlying

def get_probs(periods, u, chg):
    p = {}
    underlying = get_underlying(periods, u, chg)
    for j in range(periods):
        p[j] = []

        for i in range(j+1):
            prob = (underlying[j][i]-underlying[j+1][i+1])/(underlying[j+1][i]-underlying[j+1][i+1])
            p[j].append(prob)
            p[j].append(1-prob)

    return p

def one_up_swing(strike, periods, u, chg):
    underlying_tree = get_underlying(periods, u, chg)
    prob = get_probs(periods, u, chg)
    one_up = {}

    #the final value tree handled seperatedly
    one_up[periods] = []
    for i in range(len(underlying_tree[periods])):
        one_up[periods].append(max(0, underlying_tree[periods][i] - strike))

    #iterate to get the other values
    for i in range(periods-1, -1, -1):
        one_up[i] = []
        for j in range(len(one_up[i+1])-1):
            o = one_up[i+1][j]*prob[0][0] + one_up[i+1][j+1]*prob[0][1]
            ex = max(0, underlying_tree[i][j] - strike)

            one_up[i].append(max(o, ex))

    return one_up

def two_up_swing(strike, periods, u, chg):
    underlying_tree = get_underlying(periods, u, chg)
    prob = get_probs(periods, u, chg)
    one_up = one_up_swing(strike, periods, u, chg)
    two_up = {}

    # the final value tree handled seperatedly
    two_up[periods] = one_up[periods]

    #rest of the cases
    for i in range(periods-1, -1, -1):
        two_up[i] = []
        for j in range(len(one_up[i+1])-1):
            #assume you exercise the first option
            first_ex = max(0, underlying_tree[i][j]-strike)
            second_ex = one_up[i][j]

            #assume you don't exercise the first option
            noex = two_up[i+1][j]*prob[0][0] + two_up[i+1][j+1]*prob[0][1]

            two_up[i].append(max(first_ex + second_ex, noex))

    return two_up

def three_up_swing(strike, periods, u, chg):
    underlying_tree = get_underlying(periods, u, chg)
    prob = get_probs(periods, u, chg)
    one_up = one_up_swing(strike, periods, u, chg)
    two_up = two_up_swing(strike, periods, u, chg)
    three_up = {}

    # the final two value trees handled seperatedly
    three_up[periods] = two_up[periods]
    three_up[periods-1] = two_up[periods-1]

    #rest of the cases
    for i in range(periods-2, -1, -1):
        three_up[i] = []
        for j in range(len(one_up[i+1])-1):
            #assume you exercise the first option
            first_ex = max(0, underlying_tree[i][j]-strike)
            second_ex = two_up[i][j]

            #assume you don't exercise the first option
            noex = three_up[i+1][j]*prob[0][0] + three_up[i+1][j+1]*prob[0][1]

            three_up[i].append(max(first_ex + second_ex, noex))

    return three_up

def four_up_swing(strike, periods, u, chg):
    underlying_tree = get_underlying(periods, u, chg)
    prob = get_probs(periods, u, chg)
    one_up = one_up_swing(strike, periods, u, chg)
    two_up = two_up_swing(strike, periods, u, chg)
    three_up = three_up_swing(strike, periods, u, chg)
    four_up = {}
    diffs = {}
    opex = {}

    # the final three value trees handled seperatedly
    four_up[periods] = three_up[periods]
    four_up[periods - 1] = three_up[periods - 1]
    four_up[periods - 2] = three_up[periods - 2]

    # rest of the cases
    for i in range(periods-3, -1, -1):
        four_up[i] = []
        diffs[i] = []
        opex[i] = []
        for j in range(len(one_up[i + 1]) - 1):
            # assume you exercise the first option
            first_ex = underlying_tree[i][j] - strike
            second_ex = three_up[i][j]

            ex = first_ex + second_ex

            # assume you don't exercise the first option
            noex = four_up[i+1][j]*prob[0][0] + four_up[i+1][j+1]*prob[0][1]

            diffs[i].append(round(ex - noex, 9))

            #for each timestep determine the index where optimal exercise begins
            if ex >= noex:
                opex[i].append(j)

            four_up[i].append(max(0, ex, noex))

    return [four_up, diffs, opex]

def one_down_swing(strike, periods, u, chg):
    underlying_tree = get_underlying(periods, u, chg)
    prob = get_probs(periods, u, chg)
    one_down = {}

    #the final value tree handled seperatedly
    one_down[periods] = []
    for i in range(len(underlying_tree[periods])):
        one_down[periods].append(max(0, strike - underlying_tree[periods][i]))

    #iterate to get the other values
    for i in range(periods-1, -1, -1):
        one_down[i] = []
        for j in range(len(one_down[i+1])-1):
            o = one_down[i + 1][j] * prob[0][0] + one_down[i + 1][j + 1] * prob[0][1]
            ex = max(0, strike - underlying_tree[i][j])

            one_down[i].append(max(o, ex))

    return one_down

def two_down_swing(strike, periods, u, chg):
    underlying_tree = get_underlying(periods, u, chg)
    prob = get_probs(periods, u, chg)
    one_down = one_down_swing(strike, periods, u, chg)
    two_down = {}

    # the final value tree handled seperatedly
    two_down[periods] = one_down[periods]

    #rest of the cases
    for i in range(periods-1, -1, -1):
        two_down[i] = []
        for j in range(len(one_down[i+1])-1):
            #assume you exercise the first option
            first_ex = max(0, strike - underlying_tree[i][j])
            second_ex = one_down[i][j]

            #assume you don't exercise the first option
            noex = two_down[i+1][j]*prob[0][0] + two_down[i+1][j+1]*prob[0][1]

            two_down[i].append(max(first_ex + second_ex, noex))

    return two_down

def three_down_swing(strike, periods, u, chg):
    underlying_tree = get_underlying(periods, u, chg)
    prob = get_probs(periods, u, chg)
    one_down = one_down_swing(strike, periods, u, chg)
    two_down = two_down_swing(strike, periods, u, chg)
    three_down = {}

    # the final two value trees handled seperatedly
    three_down[periods] = two_down[periods]
    three_down[periods-1] = two_down[periods-1]

    #rest of the cases
    for i in range(periods-2, -1, -1):
        three_down[i] = []
        for j in range(len(one_down[i+1])-1):
            #assume you exercise the first option
            first_ex = max(0, strike - underlying_tree[i][j])
            second_ex = two_down[i][j]

            #assume you don't exercise the first option
            noex = three_down[i+1][j]*prob[0][0] + three_down[i+1][j+1]*prob[0][1]

            three_down[i].append(max(first_ex + second_ex, noex))

    return three_down

def four_down_swing(strike, periods, u, chg):
    underlying_tree = get_underlying(periods, u, chg)
    prob = get_probs(periods, u, chg)
    one_down = one_down_swing(strike, periods, u, chg)
    two_down = two_down_swing(strike, periods, u, chg)
    three_down = three_down_swing(strike, periods, u, chg)
    four_down = {}
    diffs = {}
    opex = {}

    # the final three value trees handled seperatedly
    four_down[periods] = three_down[periods]
    four_down[periods - 1] = three_down[periods - 1]
    four_down[periods - 2] = three_down[periods - 2]


    # rest of the cases
    for i in range(periods-3, -1, -1):
        four_down[i] = []
        diffs[i] = []
        opex[i] = []
        for j in range(len(one_down[i + 1]) - 1):
            # assume you exercise the first option
            first_ex = strike - underlying_tree[i][j]
            second_ex = three_down[i][j]
            ex = first_ex + second_ex

            # assume you don't exercise the first option
            noex = four_down[i+1][j]*prob[0][0] + four_down[i+1][j+1]*prob[0][1]

            # impose a cut off to eliminate rounding error
            diffs[i].append(round(ex - noex, 8))

            #for each timestep, give the index of optimal exercise
            if ex >= noex:
                opex[i].append(j)

            four_down[i].append(max(0, ex, noex))

    return [four_down, diffs, opex]

#find the boundary for the down swing
print(four_down_swing(50000, 52, 50000, 1.1)[2])

underlying = get_underlying(52, 50000, 1.1)
x = list(range(25, 53))
y = []
for i in range(52, 24, -1):
    y.append(underlying[i][25])
y.reverse()

#plot the boundary for the down swing
plot1 = plt.figure(1)
plt.plot(x, y)
plt.title('Optimal Exercise Boundary for 4-Down Swing')
plt.ylabel('Gasoline Price')
plt.xlabel('Week')
plt.show()

