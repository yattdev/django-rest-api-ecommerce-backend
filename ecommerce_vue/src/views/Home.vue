<template>
  <div class="home">
    <ProduitsList msg="Welcome to Your Vue.js + TypeScript App"/>
  </div>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator';
import ProduitsList from '@/components/ProduitsList.vue'; // @ is an alias to /src

@Component({
  components: {
    ProduitsList,
  },
})
export default class Home extends Vue {}
</script>
