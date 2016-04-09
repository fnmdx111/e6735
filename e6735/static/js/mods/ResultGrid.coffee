shortid = require 'shortid'
$ = require 'jquery'
React = require 'react'
ReactDOM = require 'react-dom'
[_h5, _div, _p, _video, _source, _audio, _h4] = (React.createFactory(name)\
  for name in ['h5', 'div', 'p', 'video', 'source', 'audio', 'h4'])
videojs = require 'video.js'
AbstractView = require './AbstractView'
SimplePanel = React.createFactory(require './SimplePanel')

cls = React.createClass
  render: ->
    $$p = this.props
    video_properties =
      className: 'video-js vjs-default-skin embed-responsive-item'
      id: $$p.video_id
      width: '640'
      height: '322'
      muted: true
      preload: "auto"
      controls: true

    audio_properties =
      className: 'embed-responsive-item'
      controls: true
      preload: "auto"
      id: $$p.audio_id

    tag = switch
      when $$p.confidence < 0.333 then 'default'
      when $$p.confidence < 0.666 then 'warning'
      else 'danger'

    _div {className: 'col-md-6'},
      SimplePanel {
        class_name: tag
        title: "#{$$p.title} by #{$$p.artist}"
      },
        _h5 {}, "confidence: #{$$p.confidence}"
        _div {className: 'embed-responsive embed-responsive-16by9 mm-container'},
          _video video_properties,
            _source {src: $$p.video_fp, type: $$p.video_type},
          _audio audio_properties,
            _source {src: $$p.audio_fp, type: $$p.audio_type}

  componentDidMount: ->
    $$p = this.props

    videojs $$p.video_id, {
      bigPlayButton: false
      controlBar: {
        volumeMenuButton: false
        playToggle: false
        progressControl: false
      }
    },
    ->
      audio = $('#' + $$p.audio_id)
      video = this

      video.on 'play', ->
        audio.trigger 'play'
      video.on 'pause', ->
        audio.trigger 'pause'

      audio.on 'timeupdate', ->
        return if not this.paused
        video.trigger 'timeupdate'
      audio.on 'seeking', ->
        video.currentTime this.currentTime
      audio.on 'play', ->
        video.play()
      audio.on 'pause', ->
        video.pause()


class ResultGridInfoItem
  constructor: (title, artist, audio_fp, video_fp, sid, audio_t, video_t,
    confidence) ->
    @el = React.createElement cls,
      sid: sid
      video_fp: video_fp
      audio_fp: audio_fp
      audio_id: 'audio-player-' + sid
      video_id: 'video-player-' + sid
      title: title
      artist: artist
      key: sid  # See https://fb.me/react-warning-keys for details.
      audio_type: audio_t
      video_type: video_t
      confidence: confidence


grid_cls = React.createClass
  render: ->
    _div {className: 'row'},
      (info.el for info in @props.items)


module.exports = class ResultGrid extends AbstractView
  constructor: (id) ->
    super '.query-result', id

  render: (response, uploaded_file) ->
    # refresh_refs()
    super()

    rscp = (fp) -> response.resource_path + fp

    if response.type == 'audio'
      items = for r in response.result
        new ResultGridInfoItem r.title, r.artist, rscp(r.filename),
          window.URL.createObjectURL(uploaded_file), shortid.generate(),
          '', uploaded_file.type, r.confidence

    else
      items = for r in response.result
        new ResultGridInfoItem r.title, r.artist,
          window.URL.createObjectURL(uploaded_file), rscp(r.filename),
          shortid.generate(), uploaded_file.type, '', r.confidence

    ReactDOM.unmountComponentAtNode @anchor if @anchor?
    ReactDOM.render React.createElement(grid_cls, {items: items}),
      @anchor
