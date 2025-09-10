<template>
  <q-layout view="hHh lpr fFf">
    <q-header reveal elevated class="">
      <q-toolbar>
        <q-toolbar-title>
          <q-avatar>
            <img src="https://cdn.quasar.dev/logo-v2/svg/logo-mono-white.svg" />
          </q-avatar>

          Unimarket
        </q-toolbar-title>
      </q-toolbar>
    </q-header>

    <q-page-container class="page-container">
      <router-view />
    </q-page-container>

    <!-- quasar footer is unable to be anything but sticky - I want a nav-like footer that isn't sticky -->
    <!-- <q-footer> <q-toolbar> footer </q-toolbar> </q-footer> -->
  </q-layout>
</template>

<style scoped lang="scss">
.page-container {
  position: relative;
  max-width: 1200px;
  //   height: fit-content !important;
  //   min-height: fit-content !important;

  --vertical-spacing: 48px;
  --horizontal-spacing: 16px;
  //   margin-top: var(--vertical-spacing);
  //   margin-bottom: var(--vertical-spacing);
  margin-left: var(--horizontal-spacing);
  margin-right: var(--horizontal-spacing);

  @media (min-width: 600px) {
    --horizontal-spacing: 48px;
  }
  @media (min-width: 1024px) {
    --horizontal-spacing: 96px;
  }
  @media (min-width: 1200px) {
    --horizontal-spacing: auto;
  }
}
</style>
