<template>
  <div class="min-h-screen bg-[#1c1c1e] flex flex-col items-center justify-center px-4 gap-6 relative">
    <!-- 背景网格纹理 -->
    <div class="absolute inset-0 overflow-hidden pointer-events-none"
         style="background-image:repeating-linear-gradient(0deg,rgba(255,255,255,0.04) 0px,transparent 1px,transparent 40px,rgba(255,255,255,0.04) 41px),repeating-linear-gradient(90deg,rgba(255,255,255,0.04) 0px,transparent 1px,transparent 40px,rgba(255,255,255,0.04) 41px)">
    </div>

    <!-- 标题 -->
    <div class="relative text-center">
      <div class="inline-flex items-center justify-center w-14 h-14 bg-[#3a3a3c] border border-white/10 rounded-2xl mb-4">
        <svg class="w-7 h-7 text-[#8b92ff]" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
          <path stroke-linecap="round" stroke-linejoin="round"
            d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
        </svg>
      </div>
      <h1 class="text-2xl font-semibold text-white/95 tracking-tight">员工人事管理系统</h1>
      <p class="text-xs text-white/50 mt-1">请选择登录入口</p>
    </div>

    <!-- 入口卡片 -->
    <div class="relative w-full max-w-md grid grid-cols-1 sm:grid-cols-2 gap-4">
      <!-- 员工端 -->
      <router-link to="/login?portal=employee" class="block no-underline text-white">
        <div class="h-full bg-[#2c2c2e] border border-white/8 rounded-2xl p-6 hover:border-[#32d74b]/40 hover:bg-[#2c2c2e] transition-all duration-200 cursor-pointer group">
          <div class="w-12 h-12 bg-[#152e1a] border border-[#32d74b]/20 rounded-xl flex items-center justify-center mb-4">
            <el-icon class="text-[#32d74b] text-xl"><User /></el-icon>
          </div>
          <h2 class="text-[15px] font-semibold text-white/92 mb-1.5">员工端</h2>
          <p class="text-xs text-white/55 leading-relaxed">
            考勤打卡 · 查看工资<br>
            个人档案 · 手机适配
          </p>
          <div class="mt-4 flex items-center gap-1 text-xs text-[#32d74b]/70 font-medium group-hover:text-[#32d74b] transition-colors">
            进入
            <el-icon class="text-[10px]"><ArrowRight /></el-icon>
          </div>
        </div>
      </router-link>

      <!-- 管理员端 -->
      <router-link to="/login?portal=admin" class="block no-underline text-white">
        <div class="h-full bg-[#2c2c2e] border border-white/8 rounded-2xl p-6 hover:border-[#6b72ff]/40 transition-all duration-200 cursor-pointer group">
          <div class="w-12 h-12 bg-[#16163a] border border-[#6b72ff]/20 rounded-xl flex items-center justify-center mb-4">
            <el-icon class="text-white/70 text-xl"><Setting /></el-icon>
          </div>
          <h2 class="text-[15px] font-semibold text-white/92 mb-1.5">管理员端</h2>
          <p class="text-xs text-white/55 leading-relaxed">
            员工档案 · 工资管理<br>
            考勤确认 · 统计报表
          </p>
          <div class="mt-4 flex items-center gap-1 text-xs text-white/55 font-medium group-hover:text-white/85 transition-colors">
            进入
            <el-icon class="text-[10px]"><ArrowRight /></el-icon>
          </div>
        </div>
      </router-link>
    </div>

  </div>
</template>
