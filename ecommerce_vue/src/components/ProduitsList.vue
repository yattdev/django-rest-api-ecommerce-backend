<template>
  <div class="ProduitsList">
    <section class="jumbotron text-center">
        <div class="container">
            <h1 class="jumbotron-heading">E-COMMERCE BOOTSTRAP THEME</h1>
            <p class="lead text-muted mb-0">Simple theme for e-commerce buid with Bootstrap 4.0.0. Pages available : home, category, product, cart & contact</p>
        </div>
    </section>
    <div class="container mt-4">
        <div class="row">
            <div class="col-lg-12 col-md-12 col-sm-12 col-xs-12">
                <div class="card">
                    <div class="card-header bg-primary text-white text-uppercase">
                        <i class="fa fa-star"></i> Last products
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-lg-3 col-md-3 col-sm-6 col-xs-12"
                            v-for="produit in produitsList"
                            v-bind:key="produit.reference_produit">
                                <div class="card">
                                    <img class="card-img-top image" :src="produit.thumbnail" alt="Card image cap">
                                    <div class="card-body">
                                        <h4 class="card-title">
                                            <router-link :to="produit.absolute_url" title="View Product">{{ produit.nom_produit.substring(0,10)+"..." }}</router-link>
                                        </h4>
                                        <p class="card-text">{{ produit.description_produit.substring(0,50)+"..." }}</p>
                                        <div class="row inline">
                                            <div class="col-lg-5 col-md-6 col-sm-6 col-xs-12 btn btn-danger btn-block price">
                                                {{ produit.prix_produit}}$
                                            </div>
                                            <div class="col-lg-7 col-md-6 col-sm-6 col-xs-12 btn btn-success btn-block">
                                                Add to cart
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
  </div>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator';
import axios from "axios"

export default Vue.extend({
    name: 'ProduitsList',
    data() {
        return {
            produitsList: [],
        };
    },
    mounted(){
        this.getProduitsList();
    },
    methods: {
        getProduitsList() {
            axios
                .get('/produits/')
                .then(response => {
                        this.produitsList = response.data.results;
                        console.log(this.produitsList);
                })
                .catch(error => {
                    console.log(error)
                })
        }
    }
});
</script>

<style type="text/css" media="all">
    .image{
        margin-top: 1.25em;
        margin-right: 1.25em;
        margin-left: 1.25em;
        margin-bottom: 1.25em;
    }
    .card-text{
        text-align: justify;
        font-size: small;
    }
    .price{
        font-size: large;
    }
</style>
