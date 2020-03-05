<template>
<div :class="{'normal_frame': true, 'bordered': hasBordered}" :style="{width: width}">
  <div class="title">{{title}}<label v-if="lastUpdate">{{lastUpdate}}</label></div>
  <div class="content">
    <slot></slot>
  </div>
</div>
</template>

<script>
export default {
  name: 'normal-frame',
  props: {
    title: {
      type: String,
      required: false,
      default: ''
    },
    lastUpdate: {
      type: String,
      required: false,
      default: ''
    },
    width: {
      type: String,
      required: false,
      default: '400px'
    },
    hasBordered: {
      type: Boolean,
      required: false,
      default: true
    },
    
},
  data () {
    return {

    }
  },
  mounted () {
  },
  methods: {
  },
  computed: {
  }
}
</script>

<style lang="scss">
.normal_frame {
  position: relative;
  color: #000;
  border-radius: 2px;
}
.bordered {
  // border: solid 1px #D8DCE5;
  // border: solid 1px #f1f2f5;
  border: solid 1px #EDF0F5;
}
.normal_frame .title {
  padding: 10px 10px;
  border-bottom: dashed 1px #EFEFEF;
  text-align: left;
  font-size: 13px;
  text-decoration: underline;
  position: relative;
}
.normal_frame .title > label{
  position: absolute;
  font-size: 13px;
  right: 15px;
  top: 10px;
  color: #ABABAB;
}
.normal_frame .content { 

  padding: 10px 5px 5px 5px;
}
.normal_frame .table {
  font-size: 13px;
  background-color: white;
  color: #363636;
  border-collapse: collapse;
  border-spacing: 0;
  margin-bottom: 5px;
}

.normal_frame .table tr:nth-child(even){
  background-color: #FAFAFA;
}
.normal_frame .table tr:hover{
  background-color: #DBDBDB;
  cursor: pointer;
}
.normal_frame .table tr.selected{
  background-color: #00D1B2;
}
.normal_frame .table td,th{
  padding: 7px 4px;
}
.normal_frame .pagination {
  font-size: 13px;
}
</style>

