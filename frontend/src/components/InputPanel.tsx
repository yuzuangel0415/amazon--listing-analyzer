import { useState, useCallback } from 'react'; // React 状态和性能优化 Hook
import { useDropzone } from 'react-dropzone'; // 拖拽上传区域库
import { Globe, Link, FileText, FileSpreadsheet, Plus, Trash2, Loader2 } from 'lucide-react'; // 图标库

// ===== 输入面板组件的 Props 类型 =====
interface Props {
  onTextSubmit: (title: string, bullets: string[]) => void; // 文本提交回调
  onUrlSubmit: (url: string, asin: string, marketplace: string, proxy: string) => void; // URL/ASIN 提交回调
  onFileUpload: (file: File) => void; // 文件上传回调
  loading: boolean; // 是否正在加载中
}

// ===== 三个标签页的 ID 类型 =====
type TabId = 'text' | 'url' | 'excel';

// ===== 标签页配置：文本 / URL / Excel =====
const tabs: { id: TabId; label: string; icon: typeof FileText }[] = [
  { id: 'text', label: '粘贴文本', icon: FileText },
  { id: 'url', label: 'URL / ASIN', icon: Link },
  { id: 'excel', label: '上传 Excel', icon: FileSpreadsheet },
];

// ===== Amazon 各站点配置：支持 8 个主流站点 =====
const marketplaces = [
  { value: 'com', label: '美国 amazon.com' },
  { value: 'co.jp', label: '日本 amazon.co.jp' },
  { value: 'de', label: '德国 amazon.de' },
  { value: 'co.uk', label: '英国 amazon.co.uk' },
  { value: 'ca', label: '加拿大 amazon.ca' },
  { value: 'fr', label: '法国 amazon.fr' },
  { value: 'it', label: '意大利 amazon.it' },
  { value: 'es', label: '西班牙 amazon.es' },
];

export default function InputPanel({ onTextSubmit, onUrlSubmit, onFileUpload, loading }: Props) {
  const [activeTab, setActiveTab] = useState<TabId>('text'); // 当前选中的标签页，默认为文本输入

  // ===== 文本标签页的状态 =====
  const [title, setTitle] = useState(''); // 产品标题
  const [bullets, setBullets] = useState(['', '', '', '', '']); // 五点描述数组，默认5个空字段

  // ===== URL 标签页的状态 =====
  const [url, setUrl] = useState(''); // Amazon 产品链接
  const [asin, setAsin] = useState(''); // ASIN 编码
  const [marketplace, setMarketplace] = useState('com'); // 当前选择的站点
  const [proxy, setProxy] = useState(''); // 代理设置（可选）

  // ===== Excel 标签页的状态 =====
  const [selectedFile, setSelectedFile] = useState<File | null>(null); // 用户选择的文件

  // ===== 拖拽上传回调：接受文件后存储到状态 =====
  const onDrop = useCallback((accepted: File[]) => {
    if (accepted.length > 0) setSelectedFile(accepted[0]); // 只取第一个文件
  }, []);

  // ===== react-dropzone 配置 =====
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop, // 文件放置回调
    accept: { 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'], 'application/vnd.ms-excel': ['.xls'] }, // 只接受 Excel 文件
    maxFiles: 1, // 最多上传一个文件
  });

  // ===== 更新指定索引的卖点文本 =====
  const updateBullet = (i: number, val: string) => {
    setBullets(prev => prev.map((b, idx) => (idx === i ? val : b))); // 仅更新对应索引的值
  };

  // ===== 添加一条新的卖点输入框（最多10条） =====
  const addBullet = () => {
    if (bullets.length < 10) setBullets([...bullets, '']); // 追加一个空字符串
  };

  // ===== 删除指定索引的卖点输入框（至少保留1条） =====
  const removeBullet = (i: number) => {
    if (bullets.length > 1) setBullets(bullets.filter((_, idx) => idx !== i)); // 过滤掉被删除的项
  };

  // ===== 文本提交：过滤空白卖点后调用父组件回调 =====
  const handleTextSubmit = () => {
    const validBullets = bullets.filter(b => b.trim()); // 过滤掉只包含空格的条目
    if (title.trim() && validBullets.length > 0) {
      onTextSubmit(title.trim(), validBullets); // 传递去除首尾空格后的数据
    }
  };

  // ===== URL/ASIN 提交：至少填写其中一个即可 =====
  const handleUrlSubmit = () => {
    if (url.trim() || asin.trim()) {
      onUrlSubmit(url.trim(), asin.trim(), marketplace, proxy.trim());
    }
  };

  // ===== 文件上传提交 =====
  const handleFileSubmit = () => {
    if (selectedFile) onFileUpload(selectedFile); // 传递选中的文件
  };

  // ===== 表单验证状态：检查各标签页是否有有效输入 =====
  const isValidText = title.trim() && bullets.some(b => b.trim()); // 文本模式：标题和至少一条卖点
  const isValidUrl = url.trim() || asin.trim(); // URL模式：链接或 ASIN 至少填一个
  const isValidFile = !!selectedFile; // Excel模式：已选择文件

  return (
    <div className="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden">
      {/* ===== 标签页导航栏 ===== */}
      <div className="flex border-b border-gray-100 bg-gray-50/50">
        {tabs.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)} // 点击切换标签页
            className={`flex items-center gap-2 px-6 py-3.5 text-sm font-medium transition-colors relative ${
              activeTab === tab.id
                ? 'text-brand bg-white border-b-2 border-b-brand -mb-px' // 激活状态的底部边框高亮
                : 'text-gray-500 hover:text-gray-700' // 非激活状态
            }`}
          >
            <tab.icon className="w-4 h-4" /> {/* 标签页图标 */}
            {tab.label}
          </button>
        ))}
      </div>

      {/* ===== 标签页内容区域 ===== */}
      <div className="p-6">
        {/* ===== 文本输入标签页 ===== */}
        {activeTab === 'text' && (
          <div className="space-y-4">
            {/* 产品标题输入 */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-1.5">产品标题</label>
              <input
                type="text"
                value={title}
                onChange={e => setTitle(e.target.value)} // 受控输入框
                placeholder="输入 Amazon 产品标题..."
                className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand/20 focus:border-brand outline-none transition-all text-sm"
              />
            </div>
            {/* 五点描述输入区域 */}
            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label className="text-sm font-semibold text-gray-700">五点描述 (Bullet Points)</label>
                <span className="text-xs text-gray-400">{bullets.filter(b => b.trim()).length}/5 已填写</span> {/* 已填写的数量统计 */}
              </div>
              <div className="space-y-2">
                {bullets.map((b, i) => (
                  <div key={i} className="flex gap-2 items-start">
                    {/* 序号标记 */}
                    <span className="w-6 h-8 flex items-center justify-center text-xs font-bold text-gray-400 shrink-0">
                      {i + 1}
                    </span>
                    {/* 卖点输入框 */}
                    <input
                      type="text"
                      value={b}
                      onChange={e => updateBullet(i, e.target.value)} // 更新指定索引的卖点
                      placeholder={`第 ${i + 1} 条卖点描述...`}
                      className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand/20 focus:border-brand outline-none transition-all text-sm"
                    />
                    {/* 删除按钮：至少保留1条时显示 */}
                    {bullets.length > 1 && (
                      <button
                        onClick={() => removeBullet(i)}
                        className="w-8 h-8 flex items-center justify-center text-gray-400 hover:text-red-500 transition-colors"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    )}
                  </div>
                ))}
              </div>
              {/* 添加卖点按钮：最多10条 */}
              {bullets.length < 10 && (
                <button
                  onClick={addBullet}
                  className="mt-2 flex items-center gap-1 text-sm text-brand hover:text-brand-dark transition-colors font-medium"
                >
                  <Plus className="w-4 h-4" /> 添加卖点
                </button>
              )}
            </div>
            {/* 提交按钮：无效输入或加载中时禁用 */}
            <button
              onClick={handleTextSubmit}
              disabled={!isValidText || loading}
              className="w-full py-3 bg-brand hover:bg-brand-dark disabled:bg-gray-300 disabled:cursor-not-allowed text-white font-semibold rounded-xl transition-all text-sm"
            >
              {loading ? (
                <span className="flex items-center justify-center gap-2"><Loader2 className="w-4 h-4 animate-spin" />分析中...</span>
              ) : '开始分析'}
            </button>
          </div>
        )}

        {/* ===== URL / ASIN 输入标签页 ===== */}
        {activeTab === 'url' && (
          <div className="space-y-4">
            {/* Amazon 产品链接输入 */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-1.5">Amazon 产品链接</label>
              <div className="relative">
                <Globe className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" /> {/* 地球图标在输入框内 */}
                <input
                  type="url"
                  value={url}
                  onChange={e => setUrl(e.target.value)}
                  placeholder="https://www.amazon.com/dp/B0XXXXXXXXX"
                  className="w-full pl-10 pr-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand/20 focus:border-brand outline-none transition-all text-sm"
                />
              </div>
            </div>
            {/* 分隔线 */}
            <div className="text-center text-sm text-gray-400 font-medium">— 或者 —</div>
            {/* ASIN 编码输入（可以代替链接） */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-1.5">ASIN 编码</label>
              <input
                type="text"
                value={asin}
                onChange={e => setAsin(e.target.value.toUpperCase())} // 自动转为大写
                placeholder="B0XXXXXXXXX"
                maxLength={10} // ASIN 固定10位
                className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand/20 focus:border-brand outline-none transition-all text-sm font-mono tracking-wider"
              />
            </div>
            {/* 站点选择下拉框 */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-1.5">站点</label>
              <select
                value={marketplace}
                onChange={e => setMarketplace(e.target.value)}
                className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand/20 focus:border-brand outline-none transition-all text-sm bg-white"
              >
                {marketplaces.map(m => (
                  <option key={m.value} value={m.value}>{m.label}</option> // 遍历站点列表
                ))}
              </select>
            </div>
            {/* 代理设置：可折叠区域，默认收起 */}
            <details className="bg-gray-50 rounded-lg border border-gray-200 overflow-hidden">
              <summary className="px-4 py-2 text-xs font-medium text-gray-500 cursor-pointer hover:text-gray-700 select-none">
                代理设置（反爬用，可选）
              </summary>
              <div className="px-4 pb-3">
                <input
                  type="text"
                  value={proxy}
                  onChange={e => setProxy(e.target.value)}
                  placeholder="http://user:pass@ip:port 或 socks5://ip:port"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand/20 focus:border-brand outline-none transition-all text-xs font-mono"
                />
                <p className="text-xs text-gray-400 mt-1.5">
                  设置代理后可绕过 Amazon 对当前IP的拦截。留空则不使用代理。
                </p>
              </div>
            </details>
            {/* 提交按钮 */}
            <button
              onClick={handleUrlSubmit}
              disabled={!isValidUrl || loading}
              className="w-full py-3 bg-brand hover:bg-brand-dark disabled:bg-gray-300 disabled:cursor-not-allowed text-white font-semibold rounded-xl transition-all text-sm"
            >
              {loading ? (
                <span className="flex items-center justify-center gap-2"><Loader2 className="w-4 h-4 animate-spin" />抓取分析中...</span>
              ) : '抓取并分析'}
            </button>
          </div>
        )}

        {/* ===== Excel 文件上传标签页 ===== */}
        {activeTab === 'excel' && (
          <div className="space-y-4">
            {/* 拖拽上传区域：使用 react-dropzone 库 */}
            <div
              {...getRootProps()} // 绑定拖拽区域的属性和事件
              className={`border-2 border-dashed rounded-xl p-10 text-center cursor-pointer transition-all ${
                isDragActive
                  ? 'border-brand bg-brand/5' // 拖拽悬停时的高亮样式
                  : 'border-gray-300 hover:border-gray-400 bg-gray-50/50' // 默认样式
              }`}
            >
              <input {...getInputProps()} /> {/* 隐藏的原生文件输入框 */}
              <FileSpreadsheet className="w-10 h-10 mx-auto mb-3 text-gray-400" /> {/* Excel 图标 */}
              {selectedFile ? (
                <div>
                  <p className="text-sm font-semibold text-gray-700">{selectedFile.name}</p> {/* 文件名 */}
                  <p className="text-xs text-gray-400 mt-1">{(selectedFile.size / 1024).toFixed(1)} KB</p> {/* 文件大小 */}
                  <p className="text-xs text-brand mt-2 font-medium">点击更换文件</p>
                </div>
              ) : isDragActive ? (
                <p className="text-sm font-medium text-brand">释放文件以上传</p> // 拖拽悬停提示
              ) : (
                <div>
                  <p className="text-sm font-medium text-gray-600">拖拽 Excel 文件到此处</p>
                  <p className="text-xs text-gray-400 mt-1">或点击选择文件 (.xlsx, .xls)</p>
                </div>
              )}
            </div>
            {/* Excel 格式说明 */}
            <div className="bg-blue-50 rounded-lg p-3 text-xs text-blue-700">
              <p className="font-semibold mb-1">Excel 格式要求:</p>
              <p>列: <code className="bg-blue-100 px-1.5 py-0.5 rounded">title</code>, <code className="bg-blue-100 px-1.5 py-0.5 rounded">bullet1</code>~<code className="bg-blue-100 px-1.5 py-0.5 rounded">bullet5</code></p>
              <p className="mt-1">或: <code className="bg-blue-100 px-1.5 py-0.5 rounded">title</code>, <code className="bg-blue-100 px-1.5 py-0.5 rounded">bullets</code> (换行分隔)</p>
            </div>
            {/* 上传按钮 */}
            <button
              onClick={handleFileSubmit}
              disabled={!isValidFile || loading}
              className="w-full py-3 bg-brand hover:bg-brand-dark disabled:bg-gray-300 disabled:cursor-not-allowed text-white font-semibold rounded-xl transition-all text-sm"
            >
              {loading ? (
                <span className="flex items-center justify-center gap-2"><Loader2 className="w-4 h-4 animate-spin" />批量分析中...</span>
              ) : '上传并批量分析'}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
