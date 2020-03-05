<template>
<div class="shareholder-relation">
  <div class="row">
    <div class="col-md-12">
      <div class="tl">{{holderName}} 持有公司如下：</div>
      <div class="box">
        <vue-table :url="fetchUrl"  className="table is-striped" :showPager="true"></vue-table> 
      </div>
    </div>
  </div>
</div>
</template>

<script>
import HTTP from "@/core/fetch"
import ChartHelper from '@/core/chartHelper'
import VueTable    from '@/components/common/vue-table'
export default {
  name: 'shareholders',
  props: {
    holderName: {
      type: String,
      required: true,
      default: null
    },
    holderCategory: {
      type: Number,
      required: true,
      default: 0

    }
  },
  data () {
    return {
      fetchUrl: `/hkmainland/shareholder_relation?name=${encodeURIComponent(this.holderName)}&category=${this.holderCategory}`
    }
  },
  methods: {
    loadData () {
      if(this.holderName != null) {
        this.fetchUrl = `/hkmainland/shareholder_relation?name=${encodeURIComponent(this.holderName)}&category=${this.holderCategory}`
      }
    }
  },
  mounted () {
    this.$watch(vm => [vm.holderName, vm.holderCategory].join(), val => {
      this.loadData()
    })
    this.loadData()
  },
  components: { VueTable }
  
}
</script>
<style lang='scss'>
.el-dialog__body {
  padding: 0px 20px;
}
.tl {
  text-align: left;
  padding: 5px 0px;
}
</style>
<style lang='scss' scoped>

</style>
