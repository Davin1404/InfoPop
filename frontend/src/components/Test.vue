<script>
import axios from 'axios';
export default {
  data() {
    return {
      msg: "你好，世界！",
    };
  },  
  methods: {
    sendMessage(){
      axios.post(
        "/update-item",
        {name: "daivd", age:24},
        ).then((res) => {
          console.log(res.data);
        })
    },
    getMessage() {
      axios.get("/").then((res) => {
        this.msg = res.data;
      }).catch((err) => {
        console.error(err);
      });
    }
  }
};
</script>

<template>  
    <button @click="getMessage">一个按钮</button>
    <button @click="sendMessage">发送信息给服务器</button>
    <p>{{ msg }}</p>  
</template>