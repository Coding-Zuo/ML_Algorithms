# encoding: utf-8


"""
 CART的算法原理:
    1.CART分类树算法的最优特征选择方法
        (1)前面所学习的ID3算法，C4.5算法，在进行特征选择时，都是基于信息熵，这里面会涉及到大量的对数运算，为了缓解计算压力，CART分类树算法
        使用基尼指数来代替信息增益(比)，【基尼指数代表了数据的不纯度，值越小，不纯度越低，特征越好】
        (2)基尼指数计算方法
           (a)假设数据集中有n个类，样本点属于第i类的概率为pi,pi=第i类的样本数/总样本数，那么该数据集的基尼指数为:
           Gini(p) = 1 - sum(pi**2) ,其中i∈[1,n]  特别地，对于2分类任务，直接变形为 2×p*(1-p),计算更加简便!
           (b)如果数据集D根据特征A是否取某一特征值a,被分割成D1,D2两部分，则在特征A的条件下，集合D的基尼指数定义为:
           Gini(D,A) = |D1|/|D| * Gini(D1) + |D2|/|D| * Gini(D2), 其中|D|表示数据集D的样本个数
           # 如果特征A有两个以上的特征值，那么必须计算出Gini(D,A=a1),Gini(D,A=a2),Gini(D,A=a3)...,选择最小的那一个作为基尼指数,参与
           本轮的划分属性评选，最小的基尼指数对应的特征和特征值作为该数据集上的二元切分点!
    
    2.CART分类树算法对于连续特征和离散特征处理的改进
        (1)CART处理连续型特征
            CART分类树处理连续型特征，其思想和C4.5是相同的，都是将连续的特征离散化。唯一的区别在于在选择划分点时的度量方式不同，
            C4.5使用的是信息增益比，则CART分类树使用的是基尼系数，可参看第3个文件3_decision_tree_conclusion.py中，C4.5的描述。
        (2)CART处理离散型特征
            采用的思路是不停的二分离散特征，之前用ID3或者C4.5的时候，如果某个特征A被选座决策树节点，如果他有三种不同的属性值，那么决策树
            会建立一个三叉节点，导致决策树是多叉树，而CART决策树采用二分法，把数据集分为{A=a1,A=a2,a3},{A=a2,A=a1,a3},{A=a2,A=a1,a3}
            三种情况中的一个，找到基尼系数最小的组合，如{A=a2,A=a1,a3}，然后建立二叉节点，一个节点是A=a2的数据集，一个节点是A=a1,a3的数据集
            之后继续下去。【与ID3,C4.5不同,离散特征参与了一次节点的建立之后还可以参与，前者一个特征只能参与一次决策节点的选择】
    
    3.CART分类树建立算法的具体流程：
        算法输入：训练集D，基尼系数的阈值min_gini，样本个数的阈值max_of_samples
        算法输出：决策树T
        (1)对于当前节点的数据集为D,如果样本个数低于max_of_samples或者样本中不包含特征值，则返回决策子树，递归停止;
        (2)计算数据集D的基尼指数,如果基尼指数低于min_gini，则返回决策子树，递归停止;
        (3)计算当前节点上，各个特征的各个特征值对数据集D的基尼指数;(这里处理连续值和缺失值，与C4.5相同，只是信息增益比换成了基尼指数)
        (4)选择基尼指数最小的特征A和对应的特征值a，根据这个最优特征和最优特征值，将数据集划分为两部分D1，D2,作为左右节点;
        (5)对左右子树递归调用1~4步，生成决策树
        这里也是采用多数投票原则，递归停止时，返回类别数最多的类别，作为该叶子节点的类别
    
    4.CART回归树建立算法：
        CART回归树和CART分类树的建立算法大部分是类似的，这里只需了解二者算法不同的地方就好了
        (1)连续值的处理方法不同
            CART分类树采用的是基尼指数的大小，来度量各个划分点的优劣情况，这比较适合分类模型，对于回归模型，更常见的度量方式是方差。
            CART回归树的度量目标是，对于任意划分特征A,对应的任意划分点s,将数据集划分为D1,D2,求出D1和D2的均方差，求出使得D1与D2均方差
            之和最小时对应的特征及特征值划分点
            
        (2)决策树建立后进行预测的方式不同
            CART分类树采用多数投票原则作为当前节点的预测类别，
            而回归树输出不是类别，它采用的是用最终叶子的均值或者中位数作为当前节点的预测值
            
    5.CART树算法的剪枝
        CART比较有特色的是后剪枝法，即先生成一棵完整的决策树，然后产生所有可能剪枝后的CART树，然后使用交叉验证来检验各种剪枝的效果，
        选择泛化能力最好的剪枝策略。
        (1)剪枝，从决策树底端T0开始不断剪枝，直到T0的根节点，形成一个子树序列{T0,T1,T2,...,Tn}
     【关键】(a) 在剪枝的过程中，T0是最原始的CART树，t是T0中任意一个内部节点（内部节点与叶子节点相对立），对于任意一棵以t为根节点的
                子树Tt,其损失函数Cα(Tt)表达式为: Cα(Tt) = C(Tt)+α*|Tt|,其中α为正则化系数,是用来权衡预测误差与子树的复杂度，
                C(Tt)为训练数据的预测误差，分类树是用基尼系数度量，回归树是均方差度量，|Tt|为子树的叶子节点数;
            (b) 当α=0时,即没有进行正则化，那么不会约束子树的复杂度(不剪枝)，原始生成的CART树即为最优子树；
                当α=∞时，正则化强度达到最大，Tt的非根节点全部剪掉，即最终生成的CART树中,把t节点之下的节点全部剪掉；
                这两种都是极端情况，一般来说，α越大，子树Tt剪枝剪得越厉害，剪掉的节点数越多；
                对于固定的α值，一定存在使得损失函数Cα(T)最小的唯一子树；
    【关键】剪枝，是要找到一个合适的正则化系数α，来把以t为根节点的子树上的所有子节点去掉而不造成预测误差增大，并不是删除子树上的某几个节点而已
            (c) 对于以节点t为根节点的子树Tt,
                如果没有剪枝，以t为根节点的损失函数Cα(Tt)为
                            Cα(Tt) = C(Tt)+α*|Tt| ，|Tt|是一个常量，表示叶子节点的个数，|Tt|>=2,CART每个非叶子节点都必有两个孩子
                如果将其子树完全剪掉，仅仅保留根节点t，那么以t为单节点树的损失函数Cα(t)为
                            Cα(t) = C(t)+α
                当α=0或者α充分小时，子树Tt没有进行剪枝，剪枝前比完全剪完之后的训练误差更小，有不等式
                            C(Tt) < C(t) ,推出：Cα(Tt) < Cα(t)
                当α逐渐增大时，α*|Tt|的变化率肯定比α快，所以一定存在某个时刻，有Cα(Tt) = Cα(t)
                当α继续增大时，不等式反向，有 Cα(Tt) > Cα(t)
                重点来了，Cα(Tt)如果大于Cα(t)，那么就意味着剪枝前的误差高于剪枝后的误差，我们找到让不等式取等时的α值，这个时候，误差是
                相等的，但是剪枝后，子树的节点只剩下1个根节点，达到了我们剪枝的目的，因此我们进行剪枝。
            (d)在上面的基础上，我们对每一个内部节点t，都计算出一个对应的g(t)值(即α)，g(t) = (C(T)-C(Tt)) / (|Tt|-1),g(t)表示剪枝后，
               整体损失函数减小的程度，g(t)越小，说明剪下的枝丫越无关紧要，不会涉及到其他的内部节点!
               “当α开始缓慢增大时，总会有某棵子树该剪，其他子树不该剪的情况，即α超过了某个结点的g(t)，但还没有超过其他结点的g(t)，随着α
               不断地增大，不断地剪枝，就得到了n+1棵子树，最后一棵是由根节点组成的单节点树”
               因此，我们将g(t)从小到大排列，然后从原始的CART树T0中，分别剪下g(t)对应的每一个内部节点下面的所有节点，剪完之后的树，
               分别记为T1,T2,T3,...,Tn，剪枝操作完成
        
        (2)在剪枝得到的子树序列T0,T1,T2,...,Tn中通过交叉验证选取最优子树Tα
            具体地，利用独立的验证数据集，测试子树序列T0,T1,T2,...,Tn中，每一棵子树的平均方差或者基尼指数，最小值对应的那一棵子树，即被认为
            是最优的决策树，子树Tk确定了，对应的αk值也就确定了，即得到最优子树Tα!
"""
