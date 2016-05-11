React = require 'react'
E = require './Els'
SimplePanel = React.createFactory(require './SimplePanel')

slider = React.createClass
  render: ->
    E.div {className: "col-md-#{@props.col or 6}"},
         SimplePanel {title: @props.caption},
           E.input {id: this.props.id, type: 'range', className: 'sliderbar'}

slider = React.createFactory slider

module.exports = React.createClass
  render: ->
    dim_prefix = "dim-#{@props.id}-"
    sliders = ((slider {key: id, id: dim_prefix + id, caption: cap, col: @props.child_col}) for id, cap of {
      1: 'Psychedelic'
      2: 'Vibrant'
      3: 'Happy'
      4: 'Adorable'
      5: 'Gloomy'
      6: 'Energetic'
      7: 'Romantic'
      8: 'Violent'
    })

    sliders_row = E.div {className: "row"}, sliders

    E.div {className: "col-md-#{@props.col}"}, sliders_row
