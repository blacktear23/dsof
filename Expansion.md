# DSOF Expansion：AI Co-Research

> 本文是对 DSOF 的一次概念扩展：尝试使用 DSOF 的状态空间搜索视角，描述人与 AI 共同进行研究（Co-Research）的工作方式。

---

## 1. 从优化到研究

DSOF 最初是为了理解不同优化算法背后的共同结构而提出的。其基本抽象是一个状态空间搜索过程：

```text
State
  ↓
Candidate
  ↓
Transition
  ↓
Evaluation
  ↓
Frontier
  ↓
New State
  ↺
```

后来可以发现，这种结构并不局限于数学优化或计算机算法。研究本身也具有非常相似的结构：研究者从当前对问题的理解出发，提出候选方向，进行推导、实现或实验，通过现实反馈更新认知，然后从新的状态继续搜索。因此：

```text
Research ≈ Re-Search
```

这里的 `re` 并不仅仅意味着“再次”。真正重要的是整个探索过程的循环：

```text
State₀
  ↓
Search
  ↓
State₁
  ↓
Re-Search
  ↓
State₂
  ↺
```

每一次搜索都会改变状态，而状态的改变又会改变下一次搜索的空间。因此，研究并不是在一个固定问题空间里不断寻找答案，而是： **在搜索过程中不断改变自身状态，并在新的状态下重新搜索。**

---

## 2. Research 不只是 Generate + Validate

此前可以用一个简单的 Two-Phase 模型描述问题解决：

```text
Generate
    ↓
Validate
    ↓
Generate
    ↺
```

这个模型仍然有价值，但从 DSOF 的角度看，它并不足以描述完整的研究过程。

更完整的结构是：

```text
State
  ↓
Propose
  ↓
Prune
  ↓
Apply
  ↓
Evaluate
  ↓
Frontier
  ↓
New State
  ↺
```

这里的 `Evaluate` 不只是判断： **这个方案对不对？** 更重要的问题是： **这个方案告诉了我们什么？** 因此，一个失败的实验并不意味着搜索失败。候选方案可能被淘汰，但它产生的 Observation 会改变当前状态：

```text
Candidate
    ↓
Observation
    ↓
Updated State
    ↓
New Search
```

这也是 Research 与普通执行任务之间的重要区别。

---

## 3. Proposal 问题

在整个搜索过程中，`Propose` 是一个特别值得关注的步骤。并不是所有 Candidate 都是同一种 Candidate。可以首先区分两类。

### 3.1 Local Candidate

Local Candidate 是可以在当前 Representation 中自然产生的候选方案。它通常包括：

* 已有方案的变体；
* 参数调整；
* 直接推导；
* 已知算法；
* 熟悉的类比；
* 增量式优化。

LLM 在这一类任务上尤其有价值。它可以快速生成大量候选、进行比较，并探索当前 Representation 周围的搜索空间。可以粗略表示为：

```text
Current State
     │
     ↓
Current Representation
     │
     ├── Candidate A
     ├── Candidate B
     ├── Candidate C
     └── ...
```

---

### 3.2 Unexpected Candidate

另一类 Candidate 更有意思。它并不只是当前搜索轨迹上的一个更好的点，而可能挑战当前的：

* Representation；
* Abstraction；
* Assumptions；
* Constraints；
* Objective；
* Problem Decomposition。

因此真正值得关注的问题并不只是： 这个 **Candidate 是否更好？** 而是： **这个 Candidate 是否可能改变我们搜索的空间？** 于是可能出现：

```text
Current Representation
        │
        └────→ Unexpected Candidate
                      │
                      ↓
              New Representation
                      │
                      ↓
                New Search Space
```

也就是说： **Local Candidate 改变的是搜索空间中的位置；Unexpected Candidate 可能改变搜索空间本身。** 这也是为什么 Unexpected Proposal 不应该简单地被视为普通 Proposal 的“更有创造力版本”。它实际上是另一种操作。

---

# 4. “为什么不这样？”

Unexpected Proposal 有一种非常典型的形式： **为什么不这样？** 这个问题看起来非常简单，但其作用可能完全不同于普通的优化问题。

普通搜索：

```text
Current Representation
        │
        ├── Candidate A
        ├── Candidate B
        └── Candidate C
```

Unexpected Proposal：

```text
Current Representation
        │
        └────→ “为什么不这样？”
                    │
                    ↓
             New Representation
                    │
                    ↓
              New Search Space
```

它不是在当前轨迹上寻找更好的下一步。它是在尝试： **改变轨迹本身。** 因此，一个 Unexpected Candidate 的价值可能并不在于它最初看起来有多合理，而在于：

```text
Candidate
   ↓
Representation Change
   ↓
New Frontier
```

---

# 5. Human 与 AI 的不同角色

AI Co-Research 并不意味着 AI 替代 Researcher。更有意义的方式可能是让 Human 与 AI 在搜索过程中承担不同的角色。

### Human

人在当前阶段更重要的能力包括：

* Unexpected Candidate Proposal；
* Frontier Planning；
* Research Direction；
* Judgment；
* 对现实结果的解释；
* 识别有意义的异常；
* 判断哪个 Representation 值得继续研究。

### AI

AI 可以非常有效地承担：

* Candidate Expansion；
* Exploration；
* Formalization；
* 推导；
* Implementation；
* Simulation；
* Comparison；
* Literature Search；
* Apply；
* Counterexample Search。

因此可以得到一个互补结构：

```text
Human Proposal
       +
AI Exploration
       +
Reality Feedback
```

目标并不是让 AI 完成尽可能多的工作。目标是： **扩大研究者能够探索的有效搜索空间和搜索带宽。**

---

# 6. Unexpected Candidate 的特殊价值

研究者经常会贡献一种很难简单归结为普通 Candidate Generation 的能力： **提出当前搜索轨迹没有强烈暗示的 Candidate。** 它可能来自：

* 直觉；
* 跨领域迁移；
* 类比；
* 矛盾；
* 抽象；
* 反转某个默认假设；
* 对异常现象的观察；
* 一个看似不合理的问题。

这里的关键并不是“越离谱越好”。一个有价值的 Unexpected Candidate 通常应该同时具备：

```text
Unexpected
    +
Plausible
    +
Testable
    +
Potentially Transformative
```

也就是说： **不是产生随机的怪想法，而是寻找那些具有改变搜索方向潜力、同时又值得验证的非预期候选。**

---

# 7. TRIZ 与 Unexpected Proposal

TRIZ 可以成为生成 Unexpected Candidate 的一种辅助机制。尤其是 TRIZ 对“主要矛盾”的处理，可以用来主动挑战当前 Representation：

```text
Contradiction
      ↓
Alternative Principle
      ↓
Unexpected Candidate
      ↓
New Search
```

这里并不是说 TRIZ 是完整的 Research Methodology。它更像是一种： **主动逃离 Local Search 的 Proposal Heuristic。** 例如：

```text
Current Solution
      ↓
Contradiction
      ↓
Current Representation becomes insufficient
      ↓
Alternative Principle
      ↓
Unexpected Candidate
      ↓
New Search
```

TRIZ 只是其中一个例子。任何能够系统性地产生 Representation Change 的方法，都可能扮演类似角色。

---

# 8. Prompt 与 Search Manifold Steering

如果把 LLM 看作一个高维生成系统，那么 Prompt 不只是一个“告诉 AI 做什么”的指令。它同时改变 AI 生成 Candidate 时所处的条件空间。可以把它理解为：

```text
Current State
     +
Prompt / Framing
     ↓
Candidate Distribution
     ↓
Explored Region
```

因此，不同的 Prompt 可能诱导模型探索不同的概念区域。从这个角度看： **Prompt 可以被理解为一种 Search Manifold Steering 机制。** 例如：

```text
寻找这个问题的更好解决方案。
```

更倾向于当前空间内的优化。而：

```text
重新定义这个问题，有没有完全不同的表示方式？
```

则是在诱导 Representation Change。 进一步：

```text
当前方案依赖了哪些默认假设？
如果其中一个假设被反转，会发生什么？
```

则是在主动扩大搜索空间。这里的 “Manifold” 是一种概念模型，而不是对 LLM 内部数学结构的完整描述。真正重要的经验观察是： **改变问题的 Framing，可以显著改变模型探索的候选空间。**

---

# 9. Unexpected Candidate 甚至可能改变 Manifold

由此可以得到一个更有意思的可能性。如果 AI 被要求的不只是： **寻找当前空间里最好的 Candidate。** 而是： **寻找可能推翻当前 Representation 的 Candidate。**那么搜索目标本身就发生了变化。对于普通搜索来说：

```text
Search within M
```

而更高一层的搜索则是：

```text
Search for M → M'
```

前者是在当前空间里搜索。后者是在搜索： **如何改变搜索空间。** 因此可以区分：

```text
Search(M)
```

与：

```text
Search(M → M')
```

这可能是未来 AI Research System 值得探索的方向之一。

---

# 10. Frontier Planning

Research 中还有一个不能与 Candidate Generation 混淆的角色： **决定下一步探索哪个 Frontier。** 一个研究状态通常存在多个潜在方向：

```text
                 Frontier
              /     |      \
             /      |       \
        Exploit   Explore   Anomaly
             \      |       /
              \     |      /
               Current State
```

研究者需要决定： **下一步值得在哪里投入搜索资源？** 这并不只是： **哪个 Candidate 成功概率最高？** 还可能涉及：

* Expected Information Gain；
* Potential Impact；
* Verification Cost；
* Risk；
* Unexplored Region；
* Unresolved Contradiction；
* Representation Change Potential。

因此，在当前的 Co-Research 模型中：**Frontier Planning 仍然主要属于 Researcher 的职责。** AI 可以帮助评价和展开 Frontier，但决定： **哪个 Frontier 值得继续追** 本身就是 Research。

---

# 11. Human-AI Co-Research Loop

把这些部分放在一起，可以得到一个更完整的 Co-Research Loop：

```text
                         Current State
                               │
                ┌──────────────┴──────────────┐
                ↓                             ↓
        Local Propose                  Unexpected Propose
             AI                         Human / TRIZ
                │                             │
                └──────────────┬──────────────┘
                               ↓
                             Prune
                               ↓
                             Apply
                         Human + AI
                               ↓
                           Evaluate
                               ↓
                       Reality Feedback
                               ↓
                            Frontier
                        Human Planning
                               ↓
                         Updated State
                               │
                               └──────────────↺
```

* Prompt Steering 贯穿 AI 所负责的搜索过程。
* Unexpected Proposal 可以改变 Representation。
* Reality Feedback 则负责约束整个循环，避免研究退化成纯粹的语言空间搜索。

因此可以把整个过程概括为：

```text
State
  ↓
Propose
  ↓
Prune
  ↓
Apply
  ↓
Evaluate
  ↓
Frontier
  ↓
Re-Search
  ↺
```

其中：

```text
Human
  ├── Unexpected Proposal
  ├── Frontier Planning
  └── Judgment

AI
  ├── Candidate Expansion
  ├── Exploration
  ├── Apply
  └── Formalization
```

这不是绝对的职责划分，而是当前阶段一个具有实践价值的工作模型。

---

# 12. 一个当前的工作假设

以下内容应该被视为 **工作假设，而不是已经证明的完整理论**：

> **Research 可以被理解为一种不断更新状态的 Adaptive State-Space Search。搜索过程中，Search Space 本身也可能发生改变。Human 与 AI 可以在这个过程中承担不同角色：Human 更重要地负责 Unexpected Proposal、Frontier Planning 和 Judgment；AI 则可以大规模承担 Candidate Expansion、Exploration、Application、Formalization 等工作。**

这里并不意味着：

* Human 永远擅长前者；
* AI 永远只能做后者；
* 两者的能力边界固定不变。

它描述的是：**在当前 AI 能力条件下，一种具有实践价值的人机协作分工。**

---

# 13. Open Questions

这一模型仍然存在大量开放问题。

## AI 能否可靠地产生 Unexpected Candidate？

让 AI 产生“不同”“有创意”“反直觉”的想法并不困难。困难的是同时满足：

```text
Unexpected
    +
Plausible
    +
Testable
    +
Transformative
```

真正有价值的 Unexpectedness 与单纯 Novelty 并不是同一件事。

---

## AI 能否识别当前 Representation 已经错误？

一个更强的 Research System 可能需要识别：

> 当前 Search 已经陷入低收益区域。

然后主动寻找：

```text
Mₜ → Mₜ₊₁
```

而不是继续进行 Local Optimization。

---

## Frontier Planning 能否部分自动化？

未来的 Research System 可能维护多个并行 Frontier，并估计继续探索每个 Frontier 的价值。但一个重要问题仍然存在：

> **Frontier Selection 是否可以完全还原成一个 Objective Function？**

还是说它最终需要某种更高层次的 Judgment？

---

## Unexpected Proposal 能否被系统训练？

一个 Workflow 可以被记录和描述。但这并不意味着任何人都能直接复现其中的 Research Skill。高质量 Unexpected Candidate 可能高度依赖：

* accumulated experience；
* cross-domain knowledge；
* intuition；
* problem representation；
* domain-specific judgment。

这些能力能否系统性地训练给 Human 或 AI，本身仍然是一个开放问题。

---

# 14. 与 DSOF 的关系

DSOF 最初试图理解：

> **Optimization 的共同结构是什么？**

现在它进一步提供了一种可能的解释：

```text
Optimization ⊂ Search
```

而进一步：

```text
Research ≈ Adaptive Search
```

Human-AI Co-Research 则可以进一步表示为：

```text
Multiple Search Agents
          +
     Shared State
          +
   Reality Feedback
```

AI 的价值不一定是替代 Researcher。

它更可能首先表现为：

> **降低探索成本、扩大候选空间、提高搜索速度，并把原本隐性的推导过程显式化。**

而 Researcher 的核心职责则不一定是：

> “告诉 AI 应该怎么做。”

更重要的可能是：

> **决定什么值得搜索。**

以及：

> **提出当前搜索空间没有自然给出的那个 Candidate。**

因此，AI Co-Research 的一个核心结构可以被浓缩为：

```text
Human Unexpected Proposal
          ↓
AI Exploration
          ↓
Reality
          ↓
Updated State
          ↓
Human Frontier Planning
          ↓
Re-Search
          ↺
```

最终，真正值得关注的问题可能不是：AI 能不能替代 Researcher？而是： **Human 与 AI 能否形成一个比任意一方单独搜索都更强的 Research Loop？** 如果答案是肯定的，那么 AI 的真正价值可能并不在于成为一个更强的 Worker。而在于成为：

```text
Co-Researcher
```

参与搜索、扩展搜索，并帮助 Researcher 更快地抵达尚未探索的 Frontier。而 Research 的核心，始终是：

```text
Search
  ↓
Unexpected Proposal
  ↓
New Representation
  ↓
Re-Search
  ↺
```

`re` 的意义，不只是 again。**它意味着 Loop。**
