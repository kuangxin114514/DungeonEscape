# 挥砍时下半身继续走路 — 接 AnimBP（UE4.27）

目标：按住移动 + 左键挥砍时，**腿继续走/跑，上身播 Chop**。

Python 改不了 AnimGraph 的连线（pin 受保护），需要你在编辑器里接一次。接好后运行时会走 DefaultSlot，不再清掉 AnimBP。

## 打开资源

Content → `Characters/Player/KayKit/Animations/ABP_KayKitLocomotion`  
打开后切到 **AnimGraph**（不是 Event Graph）。

图里如果已经有一个 **Slot** 节点（名字可能是 Slot / DefaultSlot），直接用它，不要再新建。

## 接法（推荐：分层混合）

最终链路：

```
State Machine（现有走路）
    → Save Cached Pose（名字填 Loco）
Use cached pose (Loco) → Layered Blend Per Bone 的 Base Pose
Use cached pose (Loco) → Slot 的 Source
Slot → Layered Blend Per Bone 的 Blend Poses 0
Layered Blend Per Bone → Output Pose / Root
```

步骤：

1. 右键空白处 → **Save cached pose**，Cache Name 设为 `Loco`。把原来连到 Root/Output 的 **State Machine** 输出改接到这个 Save。
2. 右键 → **Use cached pose**，选 `Loco`（需要两个 Use：一个给 Base，一个给 Slot）。
3. 右键 → **Slot**，Slot Name 保持 **`DefaultSlot`**（必须叫这个，运行时按这个名字播）。
4. 右键 → **Layered blend per bone**。
5. 按上面链路连线。
6. 选中 **Layered blend per bone**：
   - Config / Layer Setup → Layer 0 → **Branch Filters** → `+`
   - **Bone Name** = `spine`（KayKit 骨架是 spine，不要写成 spine_01）
   - **Blend Depth** = `0`（spine 及其子骨骼：胸、手臂、头）
7. **Compile** → **Save**。

## 测

停 PIE → 再 Play → 地下城里 **边走边点左键**：腿应继续走，上身挥砍。

若仍全身定住：多半 Slot 没进 Layered，或 Layered 没设 `spine` 过滤。

## 说明

- 商店 E / 城门 / 回城 E 不受影响。
- 没接好以前，左键仍会挥砍，但会短暂切到单节点（脚底可能滑），属兜底。
