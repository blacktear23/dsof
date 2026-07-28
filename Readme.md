# Discrete State-Space Optimizer Framework (DSOF)

离散状态空间优化框架（DSOF）是一个认知工具 (Meta-Cognitive Framework)，该框架总结了一系列的优化算法，最终整理出来了一套抽象算法框架来描述这一类离散状态空间优化（搜索）算法的结构。

## 算法基本结构

整体算法是一个循环，直到找到目标结果为止，而每次循环的内部流程如下：

```
                 Current State
                      │
                      ▼
           1. Candidate Generation
                      │
                      ▼
          2. Rule Prune (Static Gate)
                      │
                      ▼
          3. State Transition
                      │
                      ▼
          4. Memo Prune (Knowledge Gate)
                      │
                      ▼
           5. Frontier Update
                      │
                      ▼
          6. Frontier Prune (Budget Gate)
```

算法框架伪代码：

```python
frontier = Frontier()
prules = ProposePruner()
frules = FrontierPruner()
memo = Memo()
best = None
frontier.Push(initial_state)

while True:
	state = frontier.Pop()
	
	if Goal(state):
		if Better(state, best)
			best = state
			
		if CanExit(state, best):
			return best
	
	for candidate in Propose(state):
        if prules.Match(candidate):
            continue

		new_state = state.Apply(candidate)
		if memo.Hit(new_state):
			continue
		
		memo.Update(new_state)		
		frontier.Push(new_state)
		
	frontier.Prune(frules)
```

在这个算法框架中，整个状态空间算法被分成了3个部分：

1. Candidate生成和Candidate剪枝（Propose，Propose Prune）
2. 状态生成和状态剪枝（State，Memo Prune）
3. Frontier 管理和 Frontier 剪枝（Frontier，Frontier Prune）

因此，我们需要给这个框架填充的部分就变成了以下七大组件：

* State，定义搜索空间中的状态表示（State Representation）以及状态转移（State Transition）
* Candidate，定义如何更新State
* Propose，如何根据状态生成Candidate
* ProposePruner，如何在 Candidate 生成阶段减掉无效生成
* Memo，维护搜索过程中积累的信息（Visited、Cost、Statistics 等），并提供状态查询与更新机制。
* Frontier，维护待搜索状态集合，并定义下一步状态的选择策略（Expansion Policy）
* FrontierPruner，根据资源预算（Beam Width、Bound、Simulation Budget 等）控制 Frontier 的规模。

在离散状态空间优化框架中，Candidate 与 State 明确分离，Candidate 本身不是 State，而是状态转移函数的输入。State.Apply(Candidate) 是整个框架唯一允许修改 State 的位置。

在 Frontier 中，如何对下一步搜索进行决策是很重要的一个课题。假设当 Frontier 通过一个 Score 函数来对内部的 States 进行排序时，尽量遵从先对比与目标的距离，后对比到目标的花费。如果 Frontier 的决策逻辑设计不好，会导致搜索域的不稳，从而导致不同 Prune Ratio 情况下结果不稳定。

## Decision Entropy

在离散状态空间优化框架中，决策熵（Decision Entropy） 用于度量当前搜索状态下决策的不确定性（Decision Uncertainty），而不是问题规模本身。这里引入 Entropy 这个概念是因为在离散搜索中，单纯依赖耗时（Latency）和吞吐量（Throughput）来评测优化器会导致严重的“性能幻觉（Performance Illusion）”。因为没有 Entropy 这个度量，我们不清楚算法慢是算法问题还是搜索空间太大的问题。而引入了 Entropy 之后，输入的状态与状态之间是可以进行判别的。

对于数学定义来说，Entropy 的函数会变成一个函数族，这里我不想明确给定一个 Decision Entropy 的函数定义，而这个函数本身跟问题的 Domain 也会有一定的耦合程度。而真正有价值的是 Entropy 这个概念。如果两个输入状态在 Decision Entropy 上是相等的，那么算法的运行时间应该会雷同。

## Prune Ratio

在离散状态空间优化框架中，我们会发现整个算法会有3个剪枝的位置：

1. Candidate 剪枝
2. State 剪枝
3. Frontier 剪枝

而这三个剪枝的计数和与 Propose 生成的 Candidate 综合的比值就是 Prune Ratio。而一个算法的 Prune Ratio 代表了这个算法的搜索效率。但是，剪枝率不代表最终结果的质量好坏。当我们开始使用三个 Prune Ratio 来度量算法的剪枝效率时，我们就可以指导算法的演进方向了。

## 算法覆盖度

离散状态空间优化框架本身是基于一系列优化算法总结出来的，因此你会在其中看到 A*，DP，Beam Search，MCTS，DFS，Greddy 等算法的影子。

| 算法                 | Propose          | Rule Prune     | Memo                   | State Prune       | Frontier              | Frontier Prune    |
| ------------------- | ---------------- | -------------- | ---------------------- | ----------------- | --------------------- | ----------------- |
| DFS                 | 所有后继           | 无              | 无                    | 无                | Stack(LIFO)           | 无                 |
| BFS                 | 所有后继           | 无              | Visit Set             | 无                | Queue(FIFO)           | 无                 |
| Greedy Best First   | 所有后继           | 少量             | Visit Set            | 无                | Priority Queue(h)     | 无                 |
| Uniform Cost Search | 所有后继           | 无              | Best Cost             | Dominated State   | Priority Queue(g)     | 无                 |
| Dijkstra            | 所有后继           | 无              | Distance Table        | Relaxation        | Priority Queue(g)     | 无                 |
| A*                  | 所有后继           | 少量             | Closed Set + g-score | Dominated State   | Priority Queue(f=g+h) | 无                 |
| Beam Search         | 所有后继           | 少量             | 可有可无               | 可有可无           | Priority Queue        | Beam Width        |
| Branch & Bound      | 所有后继           | Bound Rule      | Best Cost             | Bound Dominance   | Priority Queue / DFS  | Bound Cut         |
| IDA*                | 所有后继           | Threshold Rule  | 无                     | 无                | DFS Stack             | f-threshold       |
| MCTS                | Expansion Policy | UCT Rule        | Tree Statistics        | 无                | Search Tree           | Simulation Budget |
| Cascades Optimizer  | Rule Expansion   | Rule Disable    | Memo Group             | Cost Dominance    | Memo Groups           | Cost Bound        |
| Alpha-Beta          | 所有走法           | αβ Rule         | TT(Optional)           | Bound            | DFS                   | αβ Cut            |
| SAT/CDCL            | Propagation      | Unit/Pure Rule  | Clause DB              | Conflict Learning | Decision Stack        | Learned Clause    |

鉴于以上对照分析，这些算法都能在 DSOF 框架下进行解释。因此，Decision Entropy，Prune Ratio 都可以进行测量。而不同 Decision Entropy 对应的 Prune Ratio 是可以绘制成一个二维平面图来分析当前算法在不同输入状态的复杂度上的表现形式。另外，这里的 Prune Ratio 还可以进一步拆分成三部分：

* Rule Prune Ratio：Candidate 生成层的剪枝率
* Memo Prune Ratio：State 是否已经搜索过的剪枝率
* Frontier Prune Ratio：候选状态集的剪枝率

观察三个 Prune Ratio 的分布和输入状态的 Decision Entropy 可以观察算法在不同输入的运行模式，从而指导进一步地调整。

## 两个开放问题

如何度量一个算法的剪枝改进效果是一个有意思的问题。在 DSOF 框架中，可以用一个特殊的方式来对比 Frontier

```python
while True:
	state = frontier.Pop()
	
	if Goal(state):
		if Better(state, best)
			best = state
			
		if CanExit(state, best):
			return best

	frontier_a = frontier[:]
    frontier_b = frontier[:]

	for candidate in Propose(state):
        if prules.Match(candidate):
            continue

        frontier_a.Push(new_state)

		new_state = state.Apply(candidate)
		if memo.Hit(new_state):
			continue
		
		memo.Update(new_state)		
		frontier.Push(new_state)
        frontier_b.Push(new_state)
		
	frontier.Prune(frules)
    jaccard = jaccard_divergence(frontier_a, frontier_b)
    js_d = js_divergence(frontier_a, frontier_b)
```

1. 每次迭代的 Frontier 的 Jaccard 散度

可以用以下方式来计算 Frontier 的 Jaccard 散度：

```python
states_a = set(key(s) for s in frontier_a)
states_b = set(key(s) for s in frontier_b)

jaccard = len(states_a & states_b) / len(states_a | states_b)
```

该 Jaccard 散度代表了不同剪枝算法对状态内容的影响。

2. 每次迭代的 Frontier 的 JS 散度

可以用以下方式来计算 Frontier 的 JS 散度：

```python
PA = frontier_distribution(frontier_a)
PB = frontier_distribution(frontier_b)

P, Q = merge_distribution(PA, PB)
M = [(p + q) / 2 for p, q in zip(P, Q)]

return (kl_divergence(P, M) + kl_divergence(Q, M)) / 2
```

其中 frontier_distribution 计算方法为：

```python
weights = {}
for rank, state in enumerate(frontier):
    weights[key(state)] = math.exp(-rank / temp)

s = sum(weights.values())
for k in weights:
    weights[k] /= s

return weights
```

该方法就是计算 State 在 Frontier 的序列分布情况，然后通过计算两个不同位置生成的 Frontier 的交叉熵最终计算一个 JS 散度。

目前的发现可以计算两个散度分部值，但是其代表的意义还有待进一步研究。
