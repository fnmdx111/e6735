shortid = require 'shortid'
$ = require 'jquery'
React = require 'react'
ReactDOM = require 'react-dom'
E = require './Els'
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
      key: $$p.video_id

    audio_properties =
      className: 'embed-responsive-item'
      controls: true
      preload: "auto"
      id: $$p.audio_id
      key: $$p.audio_id

    tag = switch
      when $$p.confidence < 0.333 then 'default'
      when $$p.confidence < 0.666 then 'warning'
      else 'success'

    views = switch $$p.query_type
      when 'heterogeneous'
        [E.video video_properties,
           E.source {src: $$p.video_fp, type: $$p.video_type},
         E.audio audio_properties,
           E.source {src: $$p.audio_fp, type: $$p.audio_type}]
      when 'video'
        E.video video_properties,
          E.source {src: $$p.video_fp, type: $$p.video_type}
      when 'audio'
        E.audio audio_properties,
          E.source {src: $$p.audio_fp, type: $$p.audio_type}

    E.div {className: 'col-md-6', key: shortid.generate()},
      SimplePanel {
        class_name: tag
        title: "#{$$p.title} by #{$$p.artist}"
      },
        E.h5 {}, "confidence: #{$$p.confidence}"
        E.div {className: 'embed-responsive embed-responsive-16by9 mm-container'},
          views

  componentDidMount: ->
    $$p = this.props

    switch $$p.query_type
      when 'heterogeneous'
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
      when 'video'
        videojs $$p.video_id, {}
      when 'audio'
        true


class ResultGridInfoItem
  constructor: (title, artist, audio_fp, video_fp, sid, audio_t, video_t,
    confidence, query_type) ->
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
      query_type: query_type


grid_cls = React.createClass
  render: ->
    E.div {className: 'row'},
      (info.el for info in @props.items)


module.exports = class ResultGrid extends AbstractView
  constructor: (id) ->
    super '.query-result', id

  render: (response, uploaded_file) ->
    # refresh_refs()
    super()

    rscp = (fp) -> response.resource_path + fp

    query_type = response.query_type
    result_type = response.result_type

    if result_type == 'audio' and query_type == 'heterogeneous'
      # Uploaded file is a video clip
      items = for r in response.result
        new ResultGridInfoItem r.title, r.artist, rscp(r.filename),
          window.URL.createObjectURL(uploaded_file), shortid.generate(),
          '', uploaded_file.type, r.confidence, 'heterogeneous'

    else if result_type == 'audio' and query_type == 'homogeneous'
      # Uploaded file is an audio clip
      items = for r in response.result
        new ResultGridInfoItem(r.title, r.artist, rscp(r.filename),
          '', shortid.generate(), '', '', r.confidence, 'audio')

    else if result_type == 'video' and query_type == 'heterogeneous'
      # Uploaded file is an audio clip
      items = for r in response.result
        new ResultGridInfoItem r.title, r.artist,
          window.URL.createObjectURL(uploaded_file), rscp(r.filename),
          shortid.generate(), uploaded_file.type, '',
          r.confidence, 'heterogeneous'

    else if result_type == 'video' and query_type == 'homogeneous'
      items = for r in response.result
        new ResultGridInfoItem(r.title, r.artist, '', rscp(r.filename),
          shortid.generate(), '', '', r.confidence, 'video')

    else if query_type == 'scores'
      items = for r in response.result
        if r.type == 'audio'
          new ResultGridInfoItem(r.title, r.artist, rscp(r.filename), '',
            shortid.generate(), '', '', r.confidence, 'audio')
        else
          new ResultGridInfoItem(r.title, r.artist, '', rscp(r.filename),
            shortid.generate(), '', '', r.confidence, 'video')

    try ReactDOM.unmountComponentAtNode @anchor?
    ReactDOM.render React.createElement(grid_cls, {items: items}),
      @anchor
