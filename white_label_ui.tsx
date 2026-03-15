import React, { useState, useEffect } from 'react';
import { Settings, Eye, Calendar, Image, MessageSquare, Save, Plus, Trash2, TrendingUp, AlertCircle, CheckCircle, Activity, BarChart3, Download } from 'lucide-react';

const KVSystemsConsole = () => {
  const [clients, setClients] = useState([
    {
      id: 1,
      name: "Keen Visions Trading",
      industry: "trading",
      pageId: "941966405661933",
      pageToken: "EAARghOXjjyw...",
      features: {
        visuals: false,
        weather: false,
        cta: false,
        autoPosting: true
      },
      cadence: {
        postsPerRun: 1,
        days: ["Mon", "Wed", "Fri"],
        timeWindow: "morning"
      },
      brand: {
        tone: "operator",
        ctaStyle: "none"
      },
      stats: {
        totalPosts: 47,
        successRate: 98.5,
        lastPost: "2 hours ago"
      }
    }
  ]);

  const [activeTab, setActiveTab] = useState('dashboard');
  const [selectedClient, setSelectedClient] = useState(1);
  const [previewData, setPreviewData] = useState(null);
  const [showNotification, setShowNotification] = useState(false);

  const industries = [
    { value: "trading", label: "Trading" },
    { value: "lawn", label: "Lawn Care" },
    { value: "tax", label: "Tax Services" },
    { value: "local", label: "Local Service" },
    { value: "realestate", label: "Real Estate" }
  ];

  const tones = {
    trading: ["operator", "systems-thinking", "macro-aware", "quiet-confidence"],
    lawn: ["local-professional", "educational", "practical"],
    tax: ["professional", "reassuring", "detail-oriented"],
    local: ["friendly", "community-focused", "helpful"],
    realestate: ["professional", "aspirational", "trusted-advisor"]
  };

  const generatePreview = (client) => {
    const previews = {
      trading: {
        text: "Most traders believe movement equals opportunity.\n\nBut the real edge is knowing when to do nothing.\n\nThe market isn't punishing traders. It's exposing overactivity.",
        visual: null
      },
      lawn: {
        text: "Most lawns don't fail from neglect — they fail from cutting too short when it's hot.\n\nYour grass needs height to protect roots during heat stress.\n\nIf you want consistent care, we handle weekly maintenance and cleanups.",
        visual: "🌱 Lawn Care Tip Card"
      }
    };

    return previews[client.industry] || previews.trading;
  };

  const addNewClient = () => {
    const newClient = {
      id: Date.now(),
      name: "",
      industry: "trading",
      pageId: "",
      pageToken: "",
      features: {
        visuals: false,
        weather: false,
        cta: false,
        autoPosting: false
      },
      cadence: {
        postsPerRun: 1,
        days: [],
        timeWindow: "morning"
      },
      brand: {
        tone: "operator",
        ctaStyle: "soft"
      },
      stats: {
        totalPosts: 0,
        successRate: 0,
        lastPost: "Never"
      }
    };
    setClients([...clients, newClient]);
    setSelectedClient(newClient.id);
    setActiveTab('clients');
  };

  const updateClient = (id, field, value) => {
    setClients(clients.map(c => 
      c.id === id ? { ...c, [field]: value } : c
    ));
  };

  const updateFeature = (id, feature, value) => {
    setClients(clients.map(c => 
      c.id === id ? { 
        ...c, 
        features: { ...c.features, [feature]: value }
      } : c
    ));
  };

  const updateCadence = (id, field, value) => {
    setClients(clients.map(c => 
      c.id === id ? { 
        ...c, 
        cadence: { ...c.cadence, [field]: value }
      } : c
    ));
  };

  const updateBrand = (id, field, value) => {
    setClients(clients.map(c => 
      c.id === id ? { 
        ...c, 
        brand: { ...c.brand, [field]: value }
      } : c
    ));
  };

  const deleteClient = (id) => {
    if (window.confirm('Are you sure you want to delete this client?')) {
      setClients(clients.filter(c => c.id !== id));
      if (selectedClient === id) setSelectedClient(clients[0]?.id || null);
    }
  };

  const exportConfig = () => {
    const config = {
      default_schedule: {
        posts_per_run: 1
      },
      pages: clients.map(c => ({
        client_name: c.name,
        page_id: c.pageId,
        page_token: c.pageToken,
        brand: {
          industry: c.industry,
          tone: c.brand.tone,
          cta_style: c.brand.ctaStyle
        },
        features: {
          visuals: c.features.visuals,
          weather: c.features.weather,
          cta: c.features.cta,
          auto_posting: c.features.autoPosting
        },
        cadence: {
          posts_per_run: c.cadence.postsPerRun,
          days: c.cadence.days,
          time_window: c.cadence.timeWindow
        },
        mode_weights: c.industry === "trading" ? 
          { discipline: 60, trading: 40 } : 
          { education: 70, promotion: 30 },
        style_tags: [
          c.brand.tone,
          c.features.visuals ? "visuals-enabled" : "text-only",
          c.features.weather ? "weather-aware" : "",
          c.features.cta ? "cta-allowed" : "no-cta"
        ].filter(Boolean),
        posts_per_run: c.cadence.postsPerRun
      }))
    };

    const blob = new Blob([JSON.stringify(config, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'pages.json';
    a.click();
    
    setShowNotification(true);
    setTimeout(() => setShowNotification(false), 3000);
  };

  const currentClient = clients.find(c => c.id === selectedClient);

  // Calculate aggregate stats
  const totalClients = clients.length;
  const activeClients = clients.filter(c => c.features.autoPosting).length;
  const totalPosts = clients.reduce((sum, c) => sum + (c.stats?.totalPosts || 0), 0);
  const avgSuccessRate = clients.reduce((sum, c) => sum + (c.stats?.successRate || 0), 0) / totalClients;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Notification */}
      {showNotification && (
        <div className="fixed top-4 right-4 z-50 bg-green-500 text-white px-6 py-3 rounded-lg shadow-lg flex items-center gap-2 animate-slide-in">
          <CheckCircle className="w-5 h-5" />
          <span>Configuration exported successfully!</span>
        </div>
      )}

      {/* Header */}
      <div className="border-b border-slate-700 bg-slate-900/50 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-lg flex items-center justify-center">
                <TrendingUp className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-white">KV Systems & Automations</h1>
                <p className="text-sm text-slate-400">Social Agent Console</p>
              </div>
            </div>
            <button
              onClick={exportConfig}
              className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-blue-500 to-cyan-500 text-white rounded-lg hover:from-blue-600 hover:to-cyan-600 transition-all shadow-lg"
            >
              <Save className="w-4 h-4" />
              Export Config
            </button>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <div className="max-w-7xl mx-auto px-6 py-4">
        <div className="flex gap-4 border-b border-slate-700">
          {[
            { id: 'dashboard', label: 'Dashboard', icon: BarChart3 },
            { id: 'clients', label: 'Clients', icon: Settings },
            { id: 'preview', label: 'Preview', icon: Eye },
            { id: 'analytics', label: 'Analytics', icon: Activity }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2 font-medium transition-all ${
                activeTab === tab.id
                  ? 'text-cyan-400 border-b-2 border-cyan-400'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <tab.icon className="w-4 h-4" />
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-6 py-6">
        {/* Dashboard Tab */}
        {activeTab === 'dashboard' && (
          <div className="space-y-6">
            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-lg p-6">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-slate-400 text-sm">Total Clients</span>
                  <Settings className="w-5 h-5 text-blue-400" />
                </div>
                <div className="text-3xl font-bold text-white">{totalClients}</div>
                <div className="text-sm text-slate-400 mt-1">{activeClients} active</div>
              </div>

              <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-lg p-6">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-slate-400 text-sm">Total Posts</span>
                  <MessageSquare className="w-5 h-5 text-cyan-400" />
                </div>
                <div className="text-3xl font-bold text-white">{totalPosts}</div>
                <div className="text-sm text-slate-400 mt-1">All time</div>
              </div>

              <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-lg p-6">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-slate-400 text-sm">Success Rate</span>
                  <CheckCircle className="w-5 h-5 text-green-400" />
                </div>
                <div className="text-3xl font-bold text-white">{avgSuccessRate.toFixed(1)}%</div>
                <div className="text-sm text-slate-400 mt-1">Average</div>
              </div>

              <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-lg p-6">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-slate-400 text-sm">System Status</span>
                  <Activity className="w-5 h-5 text-green-400" />
                </div>
                <div className="text-3xl font-bold text-green-400">Online</div>
                <div className="text-sm text-slate-400 mt-1">Agent v2.0</div>
              </div>
            </div>

            {/* Client Overview */}
            <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-white mb-4">Client Overview</h3>
              <div className="space-y-3">
                {clients.map(client => (
                  <div key={client.id} className="flex items-center justify-between p-4 bg-slate-900/50 rounded-lg border border-slate-700">
                    <div className="flex items-center gap-4">
                      <div className={`w-3 h-3 rounded-full ${client.features.autoPosting ? 'bg-green-400' : 'bg-slate-600'}`} />
                      <div>
                        <div className="font-medium text-white">{client.name || 'Unnamed Client'}</div>
                        <div className="text-sm text-slate-400 capitalize">{client.industry}</div>
                      </div>
                    </div>
                    <div className="flex items-center gap-6">
                      <div className="text-right">
                        <div className="text-sm text-slate-400">Posts</div>
                        <div className="font-medium text-white">{client.stats?.totalPosts || 0}</div>
                      </div>
                      <div className="text-right">
                        <div className="text-sm text-slate-400">Success Rate</div>
                        <div className="font-medium text-green-400">{client.stats?.successRate || 0}%</div>
                      </div>
                      <button
                        onClick={() => {
                          setSelectedClient(client.id);
                          setActiveTab('clients');
                        }}
                        className="px-3 py-1 text-sm text-cyan-400 hover:bg-cyan-400/10 rounded border border-cyan-400/30"
                      >
                        Configure
                      </button>
                    </div>
                  </div>
                ))}
              </div>
              <button
                onClick={addNewClient}
                className="mt-4 w-full py-3 border-2 border-dashed border-slate-600 rounded-lg text-slate-400 hover:border-cyan-400 hover:text-cyan-400 transition-all"
              >
                + Add New Client
              </button>
            </div>
          </div>
        )}

        {/* Clients Tab */}
        {activeTab === 'clients' && (
          <div className="grid grid-cols-12 gap-6">
            {/* Client List */}
            <div className="col-span-4 bg-slate-800/50 backdrop-blur border border-slate-700 rounded-lg p-4">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-white">Clients</h2>
                <button
                  onClick={addNewClient}
                  className="p-2 text-cyan-400 hover:bg-cyan-400/10 rounded-lg"
                >
                  <Plus className="w-5 h-5" />
                </button>
              </div>
              <div className="space-y-2">
                {clients.map(client => (
                  <div
                    key={client.id}
                    onClick={() => setSelectedClient(client.id)}
                    className={`p-3 rounded-lg cursor-pointer transition-all ${
                      selectedClient === client.id
                        ? 'bg-cyan-500/20 border border-cyan-400/50'
                        : 'hover:bg-slate-700/50 border border-transparent'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <div className="font-medium text-white">
                          {client.name || 'New Client'}
                        </div>
                        <div className="text-sm text-slate-400 capitalize">
                          {client.industry}
                        </div>
                      </div>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          deleteClient(client.id);
                        }}
                        className="p-1 text-red-400 hover:bg-red-400/10 rounded"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Client Details */}
            <div className="col-span-8">
              {currentClient ? (
                <div className="space-y-6">
                  {/* Basic Info */}
                  <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-lg p-6">
                    <h3 className="text-lg font-semibold mb-4 flex items-center gap-2 text-white">
                      <Settings className="w-5 h-5 text-cyan-400" />
                      Basic Information
                    </h3>
                    <div className="space-y-4">
                      <div>
                        <label className="block text-sm font-medium text-slate-300 mb-1">
                          Client Name
                        </label>
                        <input
                          type="text"
                          value={currentClient.name}
                          onChange={(e) => updateClient(currentClient.id, 'name', e.target.value)}
                          className="w-full px-3 py-2 bg-slate-900 border border-slate-600 rounded-lg focus:ring-2 focus:ring-cyan-500 focus:border-transparent text-white"
                          placeholder="Enter client name"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-slate-300 mb-1">
                          Industry
                        </label>
                        <select
                          value={currentClient.industry}
                          onChange={(e) => updateClient(currentClient.id, 'industry', e.target.value)}
                          className="w-full px-3 py-2 bg-slate-900 border border-slate-600 rounded-lg focus:ring-2 focus:ring-cyan-500 focus:border-transparent text-white"
                        >
                          {industries.map(ind => (
                            <option key={ind.value} value={ind.value}>
                              {ind.label}
                            </option>
                          ))}
                        </select>
                      </div>
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <label className="block text-sm font-medium text-slate-300 mb-1">
                            Page ID
                          </label>
                          <input
                            type="text"
                            value={currentClient.pageId}
                            onChange={(e) => updateClient(currentClient.id, 'pageId', e.target.value)}
                            className="w-full px-3 py-2 bg-slate-900 border border-slate-600 rounded-lg focus:ring-2 focus:ring-cyan-500 focus:border-transparent text-white"
                            placeholder="Facebook Page ID"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-slate-300 mb-1">
                            Tone
                          </label>
                          <select
                            value={currentClient.brand.tone}
                            onChange={(e) => updateBrand(currentClient.id, 'tone', e.target.value)}
                            className="w-full px-3 py-2 bg-slate-900 border border-slate-600 rounded-lg focus:ring-2 focus:ring-cyan-500 focus:border-transparent text-white"
                          >
                            {(tones[currentClient.industry] || []).map(tone => (
                              <option key={tone} value={tone}>
                                {tone}
                              </option>
                            ))}
                          </select>
                        </div>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-slate-300 mb-1">
                          Page Access Token
                        </label>
                        <input
                          type="password"
                          value={currentClient.pageToken}
                          onChange={(e) => updateClient(currentClient.id, 'pageToken', e.target.value)}
                          className="w-full px-3 py-2 bg-slate-900 border border-slate-600 rounded-lg focus:ring-2 focus:ring-cyan-500 focus:border-transparent text-white"
                          placeholder="Access token (masked)"
                        />
                      </div>
                    </div>
                  </div>

                  {/* Features */}
                  <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-lg p-6">
                    <h3 className="text-lg font-semibold mb-4 flex items-center gap-2 text-white">
                      <MessageSquare className="w-5 h-5 text-cyan-400" />
                      Features
                    </h3>
                    <div className="grid grid-cols-2 gap-3">
                      {Object.entries(currentClient.features).map(([key, value]) => (
                        <label key={key} className="flex items-center gap-3 cursor-pointer p-3 rounded-lg hover:bg-slate-700/30 border border-slate-700">
                          <input
                            type="checkbox"
                            checked={value}
                            onChange={(e) => updateFeature(currentClient.id, key, e.target.checked)}
                            className="w-4 h-4 text-cyan-500 rounded focus:ring-2 focus:ring-cyan-500"
                          />
                          <span className="text-slate-200 capitalize">
                            {key.replace(/([A-Z])/g, ' $1').trim()}
                          </span>
                        </label>
                      ))}
                    </div>
                  </div>

                  {/* Cadence */}
                  <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-lg p-6">
                    <h3 className="text-lg font-semibold mb-4 flex items-center gap-2 text-white">
                      <Calendar className="w-5 h-5 text-cyan-400" />
                      Posting Cadence
                    </h3>
                    <div className="space-y-4">
                      <div>
                        <label className="block text-sm font-medium text-slate-300 mb-1">
                          Posts per Run
                        </label>
                        <input
                          type="number"
                          min="1"
                          max="5"
                          value={currentClient.cadence.postsPerRun}
                          onChange={(e) => updateCadence(currentClient.id, 'postsPerRun', parseInt(e.target.value))}
                          className="w-full px-3 py-2 bg-slate-900 border border-slate-600 rounded-lg focus:ring-2 focus:ring-cyan-500 focus:border-transparent text-white"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-slate-300 mb-2">
                          Active Days
                        </label>
                        <div className="flex gap-2">
                          {['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'].map(day => (
                            <button
                              key={day}
                              onClick={() => {
                                const days = currentClient.cadence.days.includes(day)
                                  ? currentClient.cadence.days.filter(d => d !== day)
                                  : [...currentClient.cadence.days, day];
                                updateCadence(currentClient.id, 'days', days);
                              }}
                              className={`px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                                currentClient.cadence.days.includes(day)
                                  ? 'bg-cyan-500 text-white'
                                  : 'bg-slate-700 text-slate-400 hover:bg-slate-600'
                              }`}
                            >
                              {day}
                            </button>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-lg p-12 text-center">
                  <AlertCircle className="w-12 h-12 text-slate-600 mx-auto mb-3" />
                  <p className="text-slate-400">Select a client to configure</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Preview Tab */}
        {activeTab === 'preview' && (
          <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-lg p-6">
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2 text-white">
              <Eye className="w-5 h-5 text-cyan-400" />
              Content Preview
            </h3>
            {currentClient ? (
              <div className="space-y-4">
                <div className="p-4 bg-slate-900/50 rounded-lg border border-slate-700">
                  <div className="flex items-center gap-3 mb-3">
                    <div className="w-10 h-10 bg-gradient-to-br from-cyan-500 to-blue-500 rounded-full flex items-center justify-center text-white font-bold">
                      {currentClient.name.charAt(0)}
                    </div>
                    <div>
                      <div className="font-semibold text-white">{currentClient.name}</div>
                      <div className="text-sm text-slate-400">Just now</div>
                    </div>
                  </div>
                  <p className="text-slate-200 whitespace-pre-line mb-3">
                    {generatePreview(currentClient).text}
                  </p>
                  {currentClient.features.visuals && generatePreview(currentClient).visual && (
                    <div className="bg-green-900/20 border border-green-500/30 rounded-lg p-8 text-center">
                      <Image className="w-12 h-12 mx-auto text-green-400 mb-2" />
                      <div className="text-sm text-green-400">
                        {generatePreview(currentClient).visual}
                      </div>
                    </div>
                  )}
                </div>
                <div className="text-sm text-slate-400">
                  ⚠️ This is a mock preview. Actual posts will use AI generation based on your configuration.
                </div>
              </div>
            ) : (
              <div className="text-center py-12">
                <AlertCircle className="w-12 h-12 text-slate-600 mx-auto mb-3" />
                <p className="text-slate-400">Select a client to preview content</p>
              </div>
            )}
          </div>
        )}

        {/* Analytics Tab */}
        {activeTab === 'analytics' && (
          <div className="space-y-6">
            <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-lg p-6">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                  <Activity className="w-5 h-5 text-cyan-400" />
                  Performance Analytics
                </h3>
                <button className="flex items-center gap-2 px-4 py-2 bg-slate-700 text-slate-200 rounded-lg hover:bg-slate-600">
                  <Download className="w-4 h-4" />
                  Export CSV
                </button>
              </div>
              
              <div className="text-slate-400 text-center py-12">
                Analytics data will be populated from memory.db logs.
                <br />
                Export CSV to view detailed performance metrics.
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default KVSystemsConsole;