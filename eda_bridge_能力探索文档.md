# EasyEDA AI Bridge 能力探索文档

> 基于 2026-06-10 实际探索结果。配对码有效 30 分钟，需在嘉立创 EDA 专业版中生成。

## 架构概述

```
Claude/AI Tool ──HTTP──▶ Cloudflare Tunnel ──▶ Mac本地 Bridge Server ──WebSocket──▶ EDA扩展
```

- Bridge Server 运行在 Mac 本地，通过 Cloudflare Tunnel 暴露到公网
- 配对码有效期 30 分钟
- 需要在 EDA 扩展设置中开启 **"外部交互"** 权限
- 代码在 `eda` 全局对象上执行，所有 EDA API 返回 Promise
- **限制**：不能用 `const`/`let`/`function`/`await` 顶层声明，要用 IIFE 或 `.then()`

---

## 一、库搜索 (`lib_Symbol`)

### 搜索元件

```javascript
eda.lib_Symbol.search("NE555").then(function(r) {
    // r 是数组，最多10条结果
    // 每条有: uuid, libraryUuid, classification, ordinal, name, type, description
})
```

**已验证可搜关键词**：Resistor、LED、NE555、Capacitor、STM32F103C8T6

**注意**：不要传第二个参数（limit），否则可能返回空。

### 搜索结果结构

| 字段 | 含义 | 示例 |
|------|------|------|
| `uuid` | 元件唯一 ID | `36b54ca42a524dfa...` |
| `libraryUuid` | 所属库 ID | `0819f05c4eef4c71...` |
| `name` | 元件名称 | `贴片电阻CHIPRESISTORS` |
| `type` | 类型 | `2` |
| `classification` | 分类 | — |

---

## 二、原理图元件操作 (`sch_PrimitiveComponent`)

### 读取已有元件

```javascript
// 获取所有元件 ID
eda.sch_PrimitiveComponent.getAllPrimitiveId().then(function(ids) {
    // ids 是 ID 字符串数组
})

// 获取元件详情（含坐标、编号、名称）
eda.sch_PrimitiveComponent.getAll(undefined, true).then(function(comps) {
    comps.map(function(c) {
        return {
            id: c.getState_PrimitiveId(),
            name: c.getState_Name(),
            designator: c.getState_Designator(),
            x: c.getState_X(),
            y: c.getState_Y(),
            net: c.getState_Net()
        }
    })
})
```

**已验证的 Getter**：
- `getState_PrimitiveId()` — 元件唯一标识
- `getState_Name()` — 库/符号名称
- `getState_Designator()` — 位号（R1, C2, U3...）
- `getState_X()` / `getState_Y()` — 坐标
- `getState_Net()` — 网络名

### 读取元件引脚

```javascript
eda.sch_PrimitiveComponent.getAllPinsByPrimitiveId("元件的PrimitiveId").then(function(pins) {
    pins.map(function(p) {
        return {
            pinNumber: p.getState_PinNumber(),
            pinName: p.getState_PinName()
        }
    })
})
```

**已验证的 Pin Getter**：
- `getState_PinNumber()` — 引脚编号
- `getState_PinName()` — 引脚信号名
- `getState_PinType()` — ❌ 不存在

### 交互式放置元件（需要用户点击）

```javascript
// 进入鼠标跟随模式，用户在 EDA 中点击放置
eda.sch_PrimitiveComponent.placeComponentWithMouse({
    uuid: "元件uuid",
    libraryUuid: "库uuid"
}).then(function() { /* placement mode ended */ })
```

**关键**：这个调用会**阻塞直到用户点击**，不是程序化放置。可以配合 ID 轮询检测放置完成。

### 删除元件

```javascript
eda.sch_PrimitiveComponent.delete("primitiveId").then(function() {
    // 已删除
})
```

✅ 已验证可用。

### 其他方法（存在但未充分验证）

| 方法 | 说明 |
|------|------|
| `create(data, position)` | 创建元件 — 参数格式待确定，目前返回"数据不符合规范" |
| `modify(id, changes)` | 修改元件属性 |
| `get(primitiveId)` | 获取单个元件 |
| `createNetFlag({netName, x, y})` | 创建电源/地网络标志 |
| `createNetPort({...})` | 创建网络端口 |
| `placeSymbolWithMouse(data)` | 鼠标跟随放置符号 |
| `getComponentDetail(uuid)` | 获取元件详情 — 目前返回失败 |

---

## 三、原理图连线与文字

### 连线 (`sch_PrimitiveWire`)

```javascript
// 获取所有连线
eda.sch_PrimitiveWire.getAll(true).then(function(wires) {
    // 通过 getState_Line() 获取坐标（展平或嵌套数组）
})
```

### 文字 (`sch_PrimitiveText`)

```javascript
eda.sch_PrimitiveText.getAll(true).then(function(texts) {
    // 获取所有文字对象
})
```

---

## 四、DRC 检查 (`sch_Drc`)

```javascript
eda.sch_Drc.check(false, false, true).then(function(passed) {
    // passed: true/false
})
```

参数含义待验证。

---

## 五、系统 API

### Storage（持久化存储）

```javascript
// 写入 — 同步调用
eda.sys_Storage.setExtensionUserConfig("myKey", "myValue")

// 读取 — 同步调用
var value = eda.sys_Storage.getExtensionUserConfig("myKey")
```

✅ **已验证**：写入和读取均正常，数据持久化在扩展存储中。

### Dialog（对话框）

```javascript
// 信息提示
eda.sys_Dialog.showInformationMessage("消息内容", "标题")

// 确认对话框
eda.sys_Dialog.showConfirmationMessage("确认内容", "标题")

// 输入对话框
eda.sys_Dialog.showInputDialog("提示", "标题")

// 选择对话框
eda.sys_Dialog.showSelectDialog(["选项1", "选项2"], "标题")
```

注意：Dialog 方法可能是同步的，不返回 Promise。

### Toast 消息

```javascript
eda.sys_ToastMessage.showMessage("消息文本", duration)
// duration: 0=short, 1=medium, 2=long
```

✅ 在 EDA 右下角弹出消息提示。

### 国际化

```javascript
eda.sys_I18n.text("File")  // 返回 "File"（或对应语言翻译）
```

✅ 已验证。

### 鼠标跟随提示

```javascript
eda.sys_Message.showFollowMouseTip("点击放置元件", 60000)  // 60秒超时
eda.sys_Message.removeFollowMouseTip("点击放置元件")        // 手动移除
```

配合 `placeComponentWithMouse` 使用，在鼠标旁显示操作提示。

### HTTP 请求

```javascript
eda.sys_ClientUrl.request("https://api.example.com/data", "GET")
```

---

## 六、项目管理 (`dmt_Project`)

```javascript
eda.dmt_Project.getCurrentProjectInfo().then(function(p) {
    // p.friendlyName  — 项目显示名称
    // p.uuid          — 项目 UUID
    // p.data[]        — Board/Schematic/PCB 树
    // p.data[0].schematic.page[] — 原理图页列表
    // p.data[0].pcb              — PCB 信息
})
```

✅ 返回完整项目树结构。

---

## 七、PCB 操作

```javascript
// 获取 PCB 元件
eda.pcb_PrimitiveComponent.getAll().then(function(comps) { ... })

// 获取 PCB 焊盘
eda.pcb_PrimitivePad.getAll().then(function(pads) { ... })
```

⚠️ 需要在 EDA 中打开 PCB 视图，否则返回 null。

---

## 八、实战案例：读取 ESP32 模块引脚

实际在项目中放置了一个 ESP32 模块（U1，40 引脚），成功读取了全部引脚：

```
Pin 1-6:  G01-G06
Pin 7:    GND
Pin 8-16: G07-G14, RST
Pin 17-19: 3V3
Pin 20:   GND
Pin 21-26: GND, 3V3, G14-G10
Pin 27-40: G13-G01, RST, 3V3×3, GND
```

---

## 九、已验证 ✅ vs 不可用 ❌ vs 待验证 ⚠️

| 功能 | 状态 |
|------|------|
| 库搜索 (`lib_Symbol.search`) | ✅ |
| 读取原理图元件列表 | ✅ |
| 读取元件引脚 | ✅ |
| 删除元件 | ✅ |
| Storage 读写 | ✅ |
| Toast 消息 | ✅ |
| I18n 文本 | ✅ |
| Dialog 方法列表获取 | ✅ |
| 项目信息读取 | ✅ |
| 交互式放置元件 | ✅ (需用户点击) |
| 鼠标跟随提示 | ⚠️ 文档记载，未实测 |
| DRC 检查 | ⚠️ 未完成测试 |
| 创建连线 | ⚠️ 未测试 |
| 创建网络标志 | ⚠️ 未测试 |
| 程序化创建元件 | ❌ create 参数格式待确定 |
| 元件详情获取 | ❌ getComponentDetail 失败 |
| PCB 相关操作 | ⚠️ 需打开 PCB 视图 |
| HTTP 请求 | ⚠️ 未测试 |

---

## 十、限制与注意事项

1. **配对码 30 分钟过期**，超时需重新生成
2. **不能程序化"凭空"创建元件**，`create` 方法参数格式不详，主要靠 `placeComponentWithMouse` 交互式放置
3. **EDA 必须保持运行**，bridge 是本地服务，关掉 EDA 就断了
4. **代码不能有顶层声明**（`const`/`let`/`function`/`await`），需要 IIFE 或 `.then()` 链
5. **大部分 API 返回 Promise**，除了 `sys_Storage` 是同步的
6. **搜索结果最多 10 条**，且不能用第二个参数
7. **PCB 操作需要激活 PCB 视图**，否则 getter 返回 null
